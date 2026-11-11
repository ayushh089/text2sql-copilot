import argparse
from src.database.schema_extractor import get_all_tables
from src.guardrails.sql_validator import validate_sql
from src.database.executor import run_sql
from src.database.schema_extractor import (
    format_schema_for_prompt,
    get_anchor_date,
    get_database_schema,
)
from src.prompts.sql_writer import build_system_prompt
from src.utils.llm import clean_sql, generate

ap = argparse.ArgumentParser()
ap.add_argument("question")
ap.add_argument("--show-prompt", action="store_true")
args = ap.parse_args()

schema_text = format_schema_for_prompt(get_database_schema())
system = build_system_prompt(schema_text, get_anchor_date())
if args.show_prompt:
    print(system)

sql = clean_sql(generate(system, args.question))
print("SQL:\n", sql, "\n")

check = validate_sql(sql, set(get_all_tables()))
if not check.ok:
    print("BLOCKED:", check.reason)
else:
    try:
        df = run_sql(sql)
        print(f"{len(df)} rows")
        print(df.head(20).to_string(index=False))
    except Exception as e:
        print("SQL FAILED:", e)