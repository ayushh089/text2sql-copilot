from contextlib import closing

import pandas as pd
import sqlglot
from sqlglot import exp
import time

from src.config.settings import ROW_LIMIT
from src.database.connection import get_readonly_conn

class QueryTimeoutError(Exception):
    pass

def enforce_row_limit(sql: str, max_rows: int = ROW_LIMIT) -> str:
    """
    Enforce a maximum number of returned rows
    using SQLGlot AST.
    """

    if max_rows < 1:
        raise ValueError("max_rows must be positive")

    tree = sqlglot.parse_one(sql, read="sqlite")

    existing_limit = tree.args.get("limit")

    if existing_limit is None:
        tree = tree.limit(max_rows, copy=False)

    else:
        limit_expression = existing_limit.expression

        if isinstance(limit_expression, exp.Literal):
            if not limit_expression.is_string:
                try:
                    current_limit = int(limit_expression.this)

                    if current_limit <= max_rows:
                        return tree.sql(dialect="sqlite")

                except (ValueError, TypeError):
                    pass

        # Missing, invalid, or excessive LIMIT:
        # enforce the configured maximum.
        tree = tree.limit(max_rows, copy=False)

    return tree.sql(dialect="sqlite")


def run_sql(
    sql: str, limit: int = ROW_LIMIT, timeout_seconds: int = 10
) -> pd.DataFrame:

    safe_sql = enforce_row_limit(sql, limit)

    with closing(get_readonly_conn()) as conn:

        deadline = time.monotonic() + timeout_seconds

        def should_abort():
            return 1 if time.monotonic() > deadline else 0

        # Check execution progress every 10,000 SQLite instructions.
        conn.set_progress_handler(should_abort, 10_000)

        try:
            return pd.read_sql_query(safe_sql, conn)
        except Exception as e:
            if "interrupted" in str(e).lower():
                raise QueryTimeoutError(
                    f"Query took longer than {timeout_seconds} seconds. "
                    "Add filters or avoid joins without conditions."
                ) from e
            raise