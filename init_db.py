import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "products.db"
schema = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL CHECK(price >= 0),
    image_url TEXT NOT NULL
);
"""
samples = [
    ("Everyday Backpack", "A practical backpack for classes, travel, and daily use.", 1299.00,
     "https://placehold.co/640x420?text=Backpack"),
    ("Wireless Headphones", "Comfortable headphones for music and online classes.", 1899.00,
     "https://placehold.co/640x420?text=Headphones"),
    ("Desk Lamp", "A simple LED desk lamp for your study table.", 799.00,
     "https://placehold.co/640x420?text=Desk+Lamp"),
    ("Water Bottle", "Reusable bottle for carrying water throughout the day.", 399.00,
     "https://placehold.co/640x420?text=Water+Bottle"),
    ("Notebook Set", "A set of notebooks for notes and planning.", 249.00,
     "https://placehold.co/640x420?text=Notebooks"),
    ("Wireless Mouse", "An everyday wireless mouse for your computer.", 649.00,
     "https://placehold.co/640x420?text=Mouse"),
]
with sqlite3.connect(DB_PATH) as db:
    db.executescript(schema)
    db.executescript((Path(__file__).resolve().parent / "schema.sql").read_text(encoding="utf-8"))
    count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        db.executemany(
            "INSERT INTO products (name, description, price, image_url) VALUES (?, ?, ?, ?)",
            samples
        )
print(f"Database initialized: {DB_PATH}")
