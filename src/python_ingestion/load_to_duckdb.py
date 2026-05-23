from __future__ import annotations

import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv

load_dotenv()

RAW_DIR = Path("data/raw")
DUCKDB_PATH = Path(os.getenv("DUCKDB_PATH", "data/warehouse.duckdb"))

CORE_TABLES = [
    ("customers", "customers.csv"),
    ("accounts", "accounts.csv"),
    ("transactions", "transactions.csv"),
    ("loans", "loans.csv"),
]
OPTIONAL_TABLES = [
    ("macro_indicators", "macro_indicators.csv"),
    ("cvm_funds", "cvm_funds.csv"),
]


def load_to_duckdb(db_path: Path, raw_dir: Path) -> None:
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to DuckDB
    con = duckdb.connect(str(db_path))
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

        tables = list(CORE_TABLES)
        tables.extend(
            (table_name, file_name)
            for table_name, file_name in OPTIONAL_TABLES
            if (raw_dir / file_name).exists()
        )

        for table_name, file_name in tables:
            csv_path = raw_dir / file_name
            if not csv_path.exists():
                raise FileNotFoundError(f"Missing CSV file: {csv_path}")

            # Load CSV directly using DuckDB's read_csv_auto
            con.execute(
                f"CREATE OR REPLACE TABLE raw.{table_name} AS SELECT * FROM read_csv_auto('{csv_path}');"
            )
            row_count = con.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()[0]
            print(f"Loaded raw.{table_name} into DuckDB: {row_count:,} rows")

    finally:
        con.close()


def main() -> None:
    load_to_duckdb(DUCKDB_PATH, RAW_DIR)


if __name__ == "__main__":
    main()
