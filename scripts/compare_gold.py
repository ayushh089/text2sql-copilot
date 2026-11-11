import sys

from src.database.executor import run_sql
from src.pipeline import answer

QUESTION = (
    "Identify the top 5 product categories by revenue for each customer state in 2018. "
    "Consider only delivered orders and calculate revenue as the sum of product prices "
    "(excluding freight charges). Also show the total number of unique customers who "
    "purchased from each category in that state. Rank categories within each state by "
    "revenue in descending order. Display only the top 5 categories per state, along "
    "with their revenue and unique customer count."
)

GOLD_SQL = """
WITH agg AS (
  SELECT c.customer_state AS state,
         t.product_category_name_english AS category,
         SUM(oi.price) AS revenue,
         COUNT(DISTINCT c.customer_unique_id) AS unique_customers
  FROM olist_orders_dataset o
  JOIN olist_order_items_dataset oi ON oi.order_id = o.order_id
  JOIN olist_products_dataset p ON p.product_id = oi.product_id
  JOIN product_category_name_translation t
       ON t.product_category_name = p.product_category_name
  JOIN olist_customers_dataset c ON c.customer_id = o.customer_id
  WHERE o.order_status = 'delivered'
    AND strftime('%Y', o.order_purchase_timestamp) = '2018'
  GROUP BY 1, 2
),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY state ORDER BY revenue DESC) AS rn
  FROM agg
)
SELECT state, category, revenue, unique_customers
FROM ranked WHERE rn <= 5
ORDER BY state, revenue DESC
"""


def same_result(a, b):
    """Column names aur row order ignore karo, floats ko 2 decimal tak round karo."""
    if a.shape != b.shape:
        return False
    rows_a = sorted(a.round(2).astype(str).values.tolist())
    rows_b = sorted(b.round(2).astype(str).values.tolist())
    return rows_a == rows_b


gold = run_sql(GOLD_SQL, limit=5000)
res = answer(QUESTION)

print("Steps:", " -> ".join(res.trace))
if res.df is None:
    sys.exit(f"Agent failed: {res.error}")

print("gold shape:", gold.shape, "| agent shape:", res.df.shape)
print("MATCH" if same_result(gold, res.df) else "MISMATCH")