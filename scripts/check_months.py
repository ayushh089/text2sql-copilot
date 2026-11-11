from src.database.executor import run_sql

print(run_sql("""
SELECT strftime('%Y-%m', order_purchase_timestamp) AS month,
       COUNT(*) AS orders
FROM olist_orders_dataset
GROUP BY month
ORDER BY month DESC
LIMIT 8
"""))