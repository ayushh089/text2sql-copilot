import argparse

from src.pipeline import answer, get_system_prompt

ap = argparse.ArgumentParser()
ap.add_argument("question")
ap.add_argument("--show-prompt", action="store_true")
args = ap.parse_args()

if args.show_prompt:
    print(get_system_prompt())

res = answer(args.question)
print("SQL:\n", res.sql, "\n")
print("Steps:", " -> ".join(res.trace), "\n")

if res.status == "out_of_scope":
    print("OUT OF SCOPE:", res.error)
elif res.df is not None:
    print(f"{len(res.df)} rows")
    print(res.df.head(20).to_string(index=False))
else:
    print("FAILED:", res.error)