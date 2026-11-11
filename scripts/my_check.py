from src.database.executor import run_sql

sql = """WITH filtered AS (
 SELECT
   c.customer_state AS state,
   pcnt.product_category_name_english AS category,
   oi.price AS price,
   o.customer_id AS cust_id
 FROM olist_orders_dataset o
 JOIN olist_order_items_dataset oi ON oi.order_id = o.order_id
 JOIN olist_products_dataset p ON p.product_id = oi.product_id
 JOIN product_category_name_translation pcnt ON pcnt.product_category_name = p.product_category_name
 JOIN olist_customers_dataset c ON c.customer_id = o.customer_id
 WHERE o.order_status = 'delivered'
   AND strftime('%Y', o.order_purchase_timestamp) = '2018'
)
SELECT
  state,
  category,
  revenue,
  unique_customers
FROM (
  SELECT
    state,
    category,
    SUM(price) AS revenue,
    COUNT(DISTINCT cust_id) AS unique_customers,
    ROW_NUMBER() OVER (PARTITION BY state ORDER BY SUM(price) DESC) AS rn
  FROM filtered
  GROUP BY state, category
) sub
WHERE rn <= 5
ORDER BY state, revenue DESC"""
print(len(run_sql(sql, limit=5000)))