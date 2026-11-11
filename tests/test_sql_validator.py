import pytest

from src.guardrails.sql_validator import validate_sql

TABLES = {"olist_orders_dataset", "olist_customers_dataset"}

SAFE = [
    "SELECT COUNT(*) FROM olist_orders_dataset;",
    "SELECT o.order_id FROM olist_orders_dataset o JOIN olist_customers_dataset c ON o.customer_id = c.customer_id LIMIT 5",
    "WITH x AS (SELECT order_id FROM olist_orders_dataset) SELECT * FROM x",
    "SELECT order_id FROM olist_orders_dataset UNION SELECT order_id FROM olist_orders_dataset",
]

UNSAFE = [
    "DROP TABLE olist_orders_dataset",
    "DELETE FROM olist_orders_dataset",
    "UPDATE olist_orders_dataset SET order_status = 'x'",
    "INSERT INTO olist_orders_dataset VALUES (1)",
    "SELECT 1; DROP TABLE olist_orders_dataset",
    "PRAGMA table_info(olist_orders_dataset)",
    "ATTACH DATABASE 'x.db' AS x",
    "SELECT * FROM sqlite_master",
    "SELECT * FROM some_unknown_table",
    "",
    "   ",
    "hello world",
]


@pytest.mark.parametrize("sql", SAFE)
def test_safe_queries_pass(sql):
    assert validate_sql(sql, TABLES).ok, sql


@pytest.mark.parametrize("sql", UNSAFE)
def test_unsafe_queries_blocked(sql):
    result = validate_sql(sql, TABLES)
    assert not result.ok, sql
    assert result.reason