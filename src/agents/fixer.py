from src.utils.llm import clean_sql, generate


def fix_sql(system_prompt: str, question: str, bad_sql: str, error: str) -> str:
    user = (
        f"Question: {question}\n\n"
        f"This SQL did not work:\n{bad_sql}\n\n"
        f"Problem: {error}\n\n"
        "Return ONLY the corrected SQLite SELECT query. "
        "Use only tables and columns from the schema."
    )
    return clean_sql(generate(system_prompt, user))