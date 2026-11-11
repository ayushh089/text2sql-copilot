

from contextlib import closing
from src.database.connection import get_readonly_conn


def get_connection():
    return get_readonly_conn()


def get_all_tables():

    with closing(get_connection()) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """)

        return [row[0] for row in cursor.fetchall()]


def get_table_schema(table_name):

    with closing(get_connection()) as conn:

        cursor = conn.cursor()

        # PRAGMA is used to inspect SQLite table columns
        cursor.execute(
            f'PRAGMA table_info("{table_name}")'
        )

        return cursor.fetchall()


def inspect_database():

    tables = get_all_tables()

    print(f"Total tables found: {len(tables)}")

    for table in tables:

        print("\n" + "=" * 50)
        print(f"TABLE: {table}")
        print("=" * 50)

        columns = get_table_schema(table)

        for column in columns:

            cid, name, data_type, not_null, default, pk = column

            print(
                f"Column: {name:<40} "
                f"Type: {data_type:<10} "
                f"PK: {pk}"
            )

def get_relationships():

    relationships = [
        {
            "from_table": "olist_orders_dataset",
            "from_column": "customer_id",
            "to_table": "olist_customers_dataset",
            "to_column": "customer_id"
        },
        {
            "from_table": "olist_order_items_dataset",
            "from_column": "order_id",
            "to_table": "olist_orders_dataset",
            "to_column": "order_id"
        },
        {
            "from_table": "olist_order_items_dataset",
            "from_column": "product_id",
            "to_table": "olist_products_dataset",
            "to_column": "product_id"
        },
        {
            "from_table": "olist_order_items_dataset",
            "from_column": "seller_id",
            "to_table": "olist_sellers_dataset",
            "to_column": "seller_id"
        },
        {
            "from_table": "olist_order_payments_dataset",
            "from_column": "order_id",
            "to_table": "olist_orders_dataset",
            "to_column": "order_id"
        },
        {
            "from_table": "olist_order_reviews_dataset",
            "from_column": "order_id",
            "to_table": "olist_orders_dataset",
            "to_column": "order_id"
        },
        {
            "from_table": "product_category_name_translation",
            "from_column": "product_category_name",
            "to_table": "olist_products_dataset",
            "to_column": "product_category_name"
        }
    ]

    return relationships

def get_database_schema():
    """
    Returns complete database schema metadata,
    including tables, columns, and relationships.
    """

    schema = {
        "tables": [],
        "relationships": get_relationships()
    }

    for table_name in get_all_tables():
        columns = get_table_schema(table_name)

        table_info = {
            "table_name": table_name,
            "columns": []
        }

        for column in columns:
            cid, name, data_type, not_null, default, pk = column

            column_info = {
                "column_name": name,
                "data_type": data_type,
                "not_null": bool(not_null),
                "is_primary_key": bool(pk)
            }

            table_info["columns"].append(column_info)

        schema["tables"].append(table_info)

    return schema

SKIP_SAMPLE_COLUMNS = {"review_comment_title", "review_comment_message"}

def skip_samples(column_name):
    return column_name.endswith("_id") or column_name in SKIP_SAMPLE_COLUMNS

def get_sample_values(table_name, column_name, limit=3, max_all=10):
    with closing(get_connection()) as conn:
        rows = conn.execute(
            f'SELECT DISTINCT "{column_name}" FROM "{table_name}" '
            f'WHERE "{column_name}" IS NOT NULL LIMIT {max_all + 1}'
        ).fetchall()
    values = [r[0] for r in rows]
    complete = len(values) <= max_all      # kam values hain to saari mil gayi
    return (values if complete else values[:limit]), complete


def validate_relationships(schema):
    cols = {
        t["table_name"]: {c["column_name"] for c in t["columns"]}
        for t in schema["tables"]
    }
    problems = []
    for r in schema["relationships"]:
        for side in ("from", "to"):
            t, c = r[f"{side}_table"], r[f"{side}_column"]
            if t not in cols:
                problems.append(f"missing table: {t}")
            elif c not in cols[t]:
                problems.append(f"missing column: {t}.{c}")
    return problems


def format_schema_for_prompt(schema, with_samples=True):
    lines = []
    for table in schema["tables"]:
        lines.append(f"Table {table['table_name']}")
        for col in table["columns"]:
            line = f"  - {col['column_name']} ({col['data_type']})"
            if with_samples and not skip_samples(col["column_name"]):
                vals, complete = get_sample_values(
                    table["table_name"], col["column_name"]
                )
                if vals:
                    label = "values" if complete else "e.g."
                    line += f"  {label}: " + ", ".join(str(v)[:30] for v in vals)
            lines.append(line)
        lines.append("")
    lines.append("Relationships:")
    for r in schema["relationships"]:
        lines.append(
            f"  {r['from_table']}.{r['from_column']} = "
            f"{r['to_table']}.{r['to_column']}"
        )
    return "\n".join(lines)

def get_anchor_date():
    """First day of the month after the latest COMPLETE month.
    A month counts as complete if it has at least half the median
    monthly order count."""
    with closing(get_connection()) as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-%m', order_purchase_timestamp) AS m, COUNT(*)
            FROM olist_orders_dataset
            WHERE order_purchase_timestamp IS NOT NULL
            GROUP BY m ORDER BY m
        """).fetchall()

    counts = sorted(r[1] for r in rows)
    median = counts[len(counts) // 2]
    complete = [m for m, c in rows if c >= 0.5 * median]

    year, month = map(int, complete[-1].split("-"))
    year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return f"{year:04d}-{month:02d}-01"

if __name__ == "__main__":
    schema = get_database_schema()
    inspect_database()

    print("\n========== RELATIONSHIPS ==========")

    for relation in get_relationships():
        print(
            f"{relation['from_table']}.{relation['from_column']}"
            f" -> "
            f"{relation['to_table']}.{relation['to_column']}"
        )
    print("\n========== SCHEMA SUMMARY ==========")
    print("Total tables:", len(schema["tables"]))
    print("Total relationships:", len(schema["relationships"]))

    for table in schema["tables"]:
        print(
            f"{table['table_name']} "
            f"-> {len(table['columns'])} columns"
        )
        print("\n========== VALIDATION ==========")
    problems = validate_relationships(schema)
    print(problems if problems else "All relationships OK")

    text = format_schema_for_prompt(schema)
    print("\n========== PROMPT SCHEMA ==========")
    print(text)
    print(f"\n{len(text)} characters, about {len(text) // 4} tokens")
    print("Anchor date:", get_anchor_date())