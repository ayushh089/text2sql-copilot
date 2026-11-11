
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")


def load_column(filename, columns):
    path = DATA_DIR / filename
    return pd.read_csv(path, usecols=columns)


def check_primary_key(filename, columns):
    df = load_column(filename, columns)

    duplicates = df.duplicated(subset=columns).sum()
    nulls = df[columns].isna().any(axis=1).sum()

    print(f"\nTable: {filename}")
    print(f"Proposed PK: {columns}")
    print(f"Duplicate rows: {duplicates}")
    print(f"Rows with NULL key values: {nulls}")


def check_foreign_key(
    child_file, child_column,
    parent_file, parent_column
):
    child = load_column(child_file, [child_column])
    parent = load_column(parent_file, [parent_column])

    parent_values = set(parent[parent_column].dropna())

    non_null_child = child[child_column].dropna()
    orphan_count = (~non_null_child.isin(parent_values)).sum()

    print(
        f"\nFK: {child_file}.{child_column}"
        f" -> {parent_file}.{parent_column}"
    )
    print(f"Orphan records: {orphan_count}")


if __name__ == "__main__":

    print("========== PRIMARY KEY CHECKS ==========")

    check_primary_key(
        "olist_customers_dataset.csv", ["customer_id"]
    )

    check_primary_key(
        "olist_orders_dataset.csv", ["order_id"]
    )

    check_primary_key(
        "olist_order_items_dataset.csv",
        ["order_id", "order_item_id"]
    )

    check_primary_key(
        "olist_order_payments_dataset.csv",
        ["order_id", "payment_sequential"]
    )

    check_primary_key(
        "olist_order_reviews_dataset.csv", ["review_id"]
    )

    check_primary_key(
        "olist_products_dataset.csv", ["product_id"]
    )

    check_primary_key(
        "olist_sellers_dataset.csv", ["seller_id"]
    )

    print("\n========== FOREIGN KEY CHECKS ==========")

    check_foreign_key(
        "olist_orders_dataset.csv", "customer_id",
        "olist_customers_dataset.csv", "customer_id"
    )

    check_foreign_key(
        "olist_order_items_dataset.csv", "order_id",
        "olist_orders_dataset.csv", "order_id"
    )

    check_foreign_key(
        "olist_order_items_dataset.csv", "product_id",
        "olist_products_dataset.csv", "product_id"
    )

    check_foreign_key(
        "olist_order_items_dataset.csv", "seller_id",
        "olist_sellers_dataset.csv", "seller_id"
    )

    check_foreign_key(
        "olist_order_payments_dataset.csv", "order_id",
        "olist_orders_dataset.csv", "order_id"
    )

    check_foreign_key(
        "olist_order_reviews_dataset.csv", "order_id",
        "olist_orders_dataset.csv", "order_id"
    )
