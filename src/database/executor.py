from contextlib import closing

import pandas as pd

from src.config.settings import ROW_LIMIT
from src.database.connection import get_readonly_conn


def run_sql(sql: str, limit: int = ROW_LIMIT) -> pd.DataFrame:
    with closing(get_readonly_conn()) as conn:
        df = pd.read_sql_query(sql, conn)
    return df.head(limit)