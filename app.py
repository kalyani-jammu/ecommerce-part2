from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, make_response
import os
import re
import secrets
import sqlite3
import urllib.request
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from functools import wraps

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "products.db"
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "development-only-change-this-secret")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin12345")

COUNTRY_NAMES = {
    "IN": "India", "US": "United States", "GB": "United Kingdom", "DE": "Germany",
    "CA": "Canada", "AU": "Australia", "FR": "France", "JP": "Japan",
    "SG": "Singapore", "AE": "United Arab Emirates", "BR": "Brazil", "NL": "Netherlands"
}


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_extensions():
    """Create new tables without disturbing the existing product catalogue."""
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS visitors (
            visitor_id TEXT PRIMARY KEY,
            country TEXT NOT NULL DEFAULT 'Unknown',
            country_code TEXT NOT NULL DEFAULT '',
            first_seen TEXT NOT NULL,
            is_simulated INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS page_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT NOT NULL,
            page_url TEXT NOT NULL,
            visited_at TEXT NOT NULL,
            is_simulated INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_visits_date ON page_visits(visited_at);
        CREATE INDEX IF NOT EXISTS idx_visits_simulated ON page_visits(is_simulated);
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_count INTEGER NOT NULL,
            countries TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS generated_styles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            css_code TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Admin login required."}), 401
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_country_for_ip(ip_address):
    """Best-effort IP geolocation. Private/local addresses are not sent to a provider."""
    if not ip_address:
        return "Unknown", ""
    import ipaddress
    try:
        ip_obj = ipaddress.ip_address(ip_address)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved:
            return "Local / Unknown", ""
    except ValueError:
        return "Unknown", ""
    try:
        url = f"https://ipapi.co/{ip_address}/json/"
        req = urllib.request.Request(url, headers={"User-Agent": "ShopEase-Analytics/1.0"})
        with urllib.request.urlopen(req, timeout=2.5) as response:
            data = json.loads(response.read().decode("utf-8"))
        code = str(data.get("country_code", "")).upper()[:2]
        country = data.get("country_name") or COUNTRY_NAMES.get(code) or "Unknown"
        return country, code
    except Exception:
        return "Unknown", ""


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/products")
def list_products():
    search = request.args.get("search", "").strip()
    try:
        with get_db() as db:
            if search:
                pattern = f"%{search}%"
                rows = db.execute(
                    """SELECT id, name, description, price, image_url FROM products
                       WHERE name LIKE ? OR description LIKE ? ORDER BY id""", (pattern, pattern)
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT id, name, description, price, image_url FROM products ORDER BY id"
                ).fetchall()
        return jsonify([dict(row) for row in rows]), 200
    except sqlite3.Error:
        return jsonify({"error": "Unable to retrieve products."}), 500


@app.get("/api/products/<int:product_id>")
def product_details(product_id):
    if product_id <= 0:
        return jsonify({"error": "Product ID must be positive."}), 400
    try:
        with get_db() as db:
            row = db.execute(
                "SELECT id, name, description, price, image_url FROM products WHERE id = ?", (product_id,)
            ).fetchone()
        if row is None:
            return jsonify({"error": "Product not found."}), 404
        return jsonify(dict(row)), 200
    except sqlite3.Error:
        return jsonify({"error": "Unable to retrieve product."}), 500


@app.post("/api/track")
def track_visit():
    payload = request.get_json(silent=True) or {}
    visitor_id = str(payload.get("visitor_id", ""))[:80]
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", visitor_id):
        return jsonify({"error": "Invalid visitor identifier."}), 400
    page_url = str(payload.get("page_url", "/"))[:300]
    with get_db() as db:
        exists = db.execute("SELECT visitor_id FROM visitors WHERE visitor_id=? AND is_simulated=0", (visitor_id,)).fetchone()
        if not exists:
            country, code = get_country_for_ip(request.remote_addr)
            db.execute("INSERT OR IGNORE INTO visitors(visitor_id,country,country_code,first_seen,is_simulated) VALUES(?,?,?,?,0)",
                       (visitor_id, country, code, now_iso()))
        db.execute("INSERT INTO page_visits(visitor_id,page_url,visited_at,is_simulated) VALUES(?,?,?,0)",
                   (visitor_id, page_url, now_iso()))
    return jsonify({"ok": True}), 201


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if secrets.compare_digest(username, ADMIN_USERNAME) and secrets.compare_digest(password, ADMIN_PASSWORD):
            session.clear()
            session["is_admin"] = True
            session["admin_username"] = username
            return redirect(url_for("admin_dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("admin_login.html")


@app.post("/admin/logout")
@admin_required
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin")
@app.get("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin.html", active="analytics")


@app.get("/admin/css-generator")
@admin_required
def css_generator():
    return render_template("css_generator.html", active="css")


@app.get("/api/analytics/overview")
@admin_required
def analytics_overview():
    with get_db() as db:
        real_users = db.execute("SELECT COUNT(*) FROM visitors WHERE is_simulated=0").fetchone()[0]
        simulated_users = db.execute("SELECT COUNT(*) FROM visitors WHERE is_simulated=1").fetchone()[0]
        real_visits = db.execute("SELECT COUNT(*) FROM page_visits WHERE is_simulated=0").fetchone()[0]
        simulated_visits = db.execute("SELECT COUNT(*) FROM page_visits WHERE is_simulated=1").fetchone()[0]
        countries = db.execute("SELECT COUNT(DISTINCT country) FROM visitors WHERE country NOT IN ('Unknown','Local / Unknown')").fetchone()[0]
        active_since = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        active_users = db.execute("SELECT COUNT(DISTINCT visitor_id) FROM page_visits WHERE visited_at >= ? AND is_simulated=0", (active_since,)).fetchone()[0]
    return jsonify({"real_users": real_users, "simulated_users": simulated_users,
                    "real_visits": real_visits, "simulated_visits": simulated_visits,
                    "countries": countries, "active_users_5m": active_users})


@app.get("/api/analytics/countries")
@admin_required
def analytics_countries():
    source = request.args.get("source", "real")
    simulated = 1 if source == "simulated" else 0
    with get_db() as db:
        rows = db.execute("""SELECT country, country_code, COUNT(*) AS users
            FROM visitors WHERE is_simulated=? GROUP BY country,country_code ORDER BY users DESC,country""", (simulated,)).fetchall()
    total = sum(row["users"] for row in rows)
    return jsonify([{"country": r["country"], "country_code": r["country_code"], "users": r["users"],
                     "percentage": round((r["users"] / total * 100), 1) if total else 0} for r in rows])


@app.get("/api/analytics/traffic")
@admin_required
def analytics_traffic():
    source = request.args.get("source", "all")
    clause, params = ("", [])
    if source == "real": clause, params = ("WHERE is_simulated=0", [])
    elif source == "simulated": clause, params = ("WHERE is_simulated=1", [])
    with get_db() as db:
        rows = db.execute(f"""SELECT substr(visited_at,1,10) AS day, COUNT(*) AS visits
            FROM page_visits {clause} GROUP BY day ORDER BY day DESC LIMIT 7""", params).fetchall()
    data = [{"date": r["day"], "visits": r["visits"]} for r in reversed(rows)]
    return jsonify(data)


@app.post("/api/simulator/run")
@admin_required
def run_simulator():
    payload = request.get_json(silent=True) or {}
    try:
        count = int(payload.get("count", 100))
    except (TypeError, ValueError):
        return jsonify({"error": "Visitor count must be a number."}), 400
    if count < 1 or count > 5000:
        return jsonify({"error": "Choose between 1 and 5,000 simulated visitors."}), 400
    allowed = {"India": "IN", "United States": "US", "United Kingdom": "GB", "Germany": "DE",
               "Canada": "CA", "Australia": "AU", "France": "FR", "Japan": "JP", "Singapore": "SG"}
    selected = payload.get("countries") or list(allowed.keys())
    selected = [c for c in selected if c in allowed]
    if not selected:
        return jsonify({"error": "Select at least one supported country."}), 400
    created = now_iso()
    with get_db() as db:
        for i in range(count):
            country = selected[i % len(selected)]
            visitor_id = "sim_" + secrets.token_urlsafe(12)
            db.execute("INSERT INTO visitors(visitor_id,country,country_code,first_seen,is_simulated) VALUES(?,?,?,?,1)",
                       (visitor_id, country, allowed[country], created))
            db.execute("INSERT INTO page_visits(visitor_id,page_url,visited_at,is_simulated) VALUES(?,?,?,1)",
                       (visitor_id, "/", created))
        db.execute("INSERT INTO simulations(visitor_count,countries,created_at) VALUES(?,?,?)",
                   (count, ", ".join(selected), created))
    return jsonify({"ok": True, "created": count, "countries": selected,
                    "message": f"Created {count} simulated visitors. They are kept separate from real visitors."}), 201


@app.get("/api/css/saved")
@admin_required
def list_saved_css():
    with get_db() as db:
        rows = db.execute("SELECT id,name,css_code,created_at FROM generated_styles ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/css/save")
@admin_required
def save_css():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "Untitled style")).strip()[:80] or "Untitled style"
    css_code = str(payload.get("css_code", ""))[:12000]
    if not css_code.strip():
        return jsonify({"error": "CSS code cannot be empty."}), 400
    with get_db() as db:
        cursor = db.execute("INSERT INTO generated_styles(name,css_code,created_at) VALUES(?,?,?)", (name, css_code, now_iso()))
        style_id = cursor.lastrowid
    return jsonify({"ok": True, "id": style_id}), 201


if __name__ == "__main__":
    if not DB_PATH.exists():
        raise SystemExit("Database missing. Run: python init_db.py")
    init_extensions()
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
