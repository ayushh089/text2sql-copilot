import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")


def inspect_columns():

    csv_files = sorted(DATA_DIR.glob("*.csv"))

    for file in csv_files:

        print("\n" + "=" * 60)
        print(f"TABLE: {file.stem}")
        print("=" * 60)

        df = pd.read_csv(file, nrows=5)

        print("Columns:")
        for column in df.columns:
            print(f"  - {column}")

        print(f"\nSample rows: {len(df)}")
        print(df.head(2).to_string(index=False))


if __name__ == "__main__":
    inspect_columns()