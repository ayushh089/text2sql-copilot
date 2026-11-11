from dataclasses import dataclass

import sqlglot
from sqlglot import exp
from sqlglot.errors import SqlglotError

# Sirf ye statement types top-level query ho sakte hain.
ALLOWED_ROOTS = (exp.Select, exp.Union, exp.Intersect, exp.Except)


@dataclass
class ValidationResult:
    ok: bool
    reason: str = ""


def validate_sql(sql: str, allowed_tables: set[str]) -> ValidationResult:
    if not sql or not sql.strip():
        return ValidationResult(False, "Empty SQL")

    try:
        statements = [s for s in sqlglot.parse(sql, read="sqlite") if s is not None]
    except SqlglotError as e:
        return ValidationResult(False, f"SQL could not be parsed: {e}")

    if len(statements) != 1:
        return ValidationResult(False, "Exactly one SQL statement is allowed")

    tree = statements[0]
    if not isinstance(tree, ALLOWED_ROOTS):
        return ValidationResult(
            False, f"Only SELECT queries are allowed, got {type(tree).__name__}"
        )

    # WITH ... AS (...) ke naam asli tables nahi hote.
    cte_names = {cte.alias for cte in tree.find_all(exp.CTE)}
    allowed = {t.lower() for t in allowed_tables} | {c.lower() for c in cte_names}

    for table in tree.find_all(exp.Table):

    # Reject database/schema-qualified table references
        if table.db or table.catalog:
            return ValidationResult(
                False,
                f"Qualified table references are not allowed: {table}"
            )
    
        name = table.name.lower()
    
        if name not in allowed:
            return ValidationResult(
                False,
                f"Table not allowed: {table.name}"
            )

    return ValidationResult(True)