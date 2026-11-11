import sqlite3
from pathlib import Path

from src.config.settings import DB_PATH


def get_readonly_conn(db_path=DB_PATH):
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"{db_path} not found. Run scripts/load_csv_to_db.py")
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    return sqlite3.connect(uri, uri=True)