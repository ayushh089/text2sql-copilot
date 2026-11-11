from src.database.connection import get_readonly_conn

conn = get_readonly_conn()
print(conn.execute("SELECT COUNT(*) FROM olist_orders_dataset").fetchone())

try:
    conn.execute("DROP TABLE olist_orders_dataset")
except Exception as e:
    print("blocked:", e)