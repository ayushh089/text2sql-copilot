from dataclasses import dataclass, field
from functools import lru_cache

import pandas as pd

from src.agents.fixer import fix_sql
from src.database.executor import run_sql
from src.database.schema_extractor import (
    format_schema_for_prompt,
    get_all_tables,
    get_anchor_date,
    get_database_schema,
)
from src.guardrails.sql_validator import validate_sql
from src.prompts.sql_writer import build_system_prompt
from src.utils.llm import clean_sql, generate

MAX_RETRIES = 3


@lru_cache(maxsize=1)
def get_system_prompt() -> str:
    schema_text = format_schema_for_prompt(get_database_schema())
    return build_system_prompt(schema_text, get_anchor_date())


@dataclass
class Result:
    question: str
    sql: str = ""
    df: pd.DataFrame | None = None
    error: str = ""
    status: str = "failed"        # "ok", "out_of_scope" ya "failed"
    retries: int = 0
    trace: list = field(default_factory=list)

def is_out_of_scope(sql: str) -> bool:
    return sql.strip().upper().startswith("CANNOT_ANSWER")


def answer(question: str) -> Result:
    system = get_system_prompt()
    allowed = set(get_all_tables())
    res = Result(question)

    sql = clean_sql(generate(system, question))
    res.trace.append("generate")

    for attempt in range(MAX_RETRIES + 1):
        if is_out_of_scope(sql):
            res.status = "out_of_scope"
            res.error = "This question is not about the data in this database."
            res.trace.append("out_of_scope")
            return res

        res.sql = sql
        check = validate_sql(sql, allowed)
        if check.ok:
            try:
                res.df = run_sql(sql)
                res.error = ""
                res.status = "ok"
                res.trace.append("execute: ok")
                return res
            except Exception as e:
                error = f"Database error: {e}"
        else:
            error = f"Validation failed: {check.reason}"

        res.error = error
        res.trace.append(f"failed: {error}")
        if attempt == MAX_RETRIES:
            break
        sql = fix_sql(system, question, sql, error)
        res.retries += 1
        res.trace.append(f"fix #{res.retries}")

    return res