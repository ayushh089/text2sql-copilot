import time

from src.database.executor import run_sql

t = time.time()
try:
    run_sql("SELECT COUNT(*) FROM olist_geolocation_dataset a, olist_geolocation_dataset b")
except Exception as e:
    print("stopped:", e, f"after {time.time() - t:.1f}s")