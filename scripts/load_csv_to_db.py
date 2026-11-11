import pandas as pd
import sqlite3
from pathlib import Path


DB_PATH=Path("data/olist.db")

DATA_DIR=Path("data/raw")



def load_csv_to_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV files found!")
    conn=sqlite3.connect(DB_PATH)
    
    
    try:
        for files in csv_files:
            file_name=files.stem
            print(f"LOADING: {file_name}")
            
            df=pd.read_csv(files)
            
            df.to_sql(
                file_name,
                conn,
                if_exists="replace",
                index=False
            )
            
            print(f"LOADED: {file_name} ({len(df)} rows)")
        print(f"\nAll CSV files loaded into {DB_PATH}")
    except Exception as e:
        print(f"Error loading {files.name}: {e}")
    finally:
        conn.close()
        
if __name__=="__main__":
    load_csv_to_db()