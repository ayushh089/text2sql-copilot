import sqlite3
from pathlib import Path


DB_PATH = Path("data/olist.db")
conn=sqlite3.connect(DB_PATH)

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

for (t,) in tables:
    n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    print(t, n)