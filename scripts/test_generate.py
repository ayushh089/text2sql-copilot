from src.utils.llm import generate, clean_sql

print(generate("You are a helpful assistant.", "Reply with one word: ready"))
print(clean_sql("```sql\nSELECT 1;\n```"))