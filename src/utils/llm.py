import re

from groq import Groq

from src.config.settings import LLM_MODEL

_client = Groq()  # GROQ_API_KEY .env se aati hai


def generate(system: str, user: str, temperature: float = 0.0) -> str:
    resp = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=800,
    )
    return resp.choices[0].message.content


def clean_sql(text: str) -> str:
    """LLM aksar SQL ko ```sql ... ``` me wrap kar deta hai. Wo hata do."""
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, re.S | re.I)
    return (m.group(1) if m else text).strip()