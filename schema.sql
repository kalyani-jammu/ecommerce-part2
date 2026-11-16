CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL CHECK(price >= 0),
    image_url TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS visitors (
    visitor_id TEXT PRIMARY KEY, country TEXT NOT NULL DEFAULT 'Unknown',
    country_code TEXT NOT NULL DEFAULT '', first_seen TEXT NOT NULL,
    is_simulated INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS page_visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT, visitor_id TEXT NOT NULL,
    page_url TEXT NOT NULL, visited_at TEXT NOT NULL,
    is_simulated INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_visits_date ON page_visits(visited_at);
CREATE INDEX IF NOT EXISTS idx_visits_simulated ON page_visits(is_simulated);
CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, visitor_count INTEGER NOT NULL,
    countries TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS generated_styles (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
    css_code TEXT NOT NULL, created_at TEXT NOT NULL
);
