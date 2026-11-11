
from src.database.executor import enforce_row_limit

queries = [
    "SELECT * FROM olist_orders_dataset",
    "SELECT * FROM olist_orders_dataset LIMIT 5",
    "SELECT * FROM olist_orders_dataset LIMIT 5000",
    "SELECT COUNT(*) FROM olist_orders_dataset"
]

for query in queries:
    print("\nOriginal:", query)
    print("Limited :", enforce_row_limit(query, 1000))
