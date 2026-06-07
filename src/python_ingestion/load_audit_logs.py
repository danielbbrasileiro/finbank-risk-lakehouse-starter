from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_engine():
    db_target = os.getenv("DB_TARGET", "").lower()
    duckdb_file = Path(os.getenv("DUCKDB_PATH", "data/warehouse.duckdb"))

    if db_target == "duckdb" and (duckdb_file.exists() or os.getenv("DUCKDB_PATH")):
        return create_engine(f"duckdb:///{duckdb_file}")

    user = os.getenv("POSTGRES_USER", "finbank")
    password = os.getenv("POSTGRES_PASSWORD", "finbank")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "finbank")

    try:
        engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as err:
        if duckdb_file.exists():
            return create_engine(f"duckdb:///{duckdb_file}")
        raise ValueError("Could not connect to Postgres and no local DuckDB found.") from err


def load_audit_logs() -> None:
    audit_path = Path(os.getenv("AI_AUDIT_PATH", "data/ai_audit/copilot_audit.jsonl"))
    if not audit_path.exists() or audit_path.stat().st_size == 0:
        print(f"No audit logs found at {audit_path}. Creating empty raw.ai_copilot_audit table.")
        records = []
    else:
        records = []
        with audit_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    df = pd.DataFrame(
        records, columns=["timestamp", "status", "question", "citations", "guarded_sql", "response"]
    )

    # Standardize column values: serialize citations list to comma-separated string
    df["citations"] = df["citations"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))

    df.to_sql(
        name="ai_copilot_audit",
        con=engine,
        schema="raw",
        if_exists="replace",
        index=False,
        chunksize=1_000,
    )
    engine.dispose()
    print(f"Loaded raw.ai_copilot_audit: {len(df):,} rows")


def main() -> None:
    load_audit_logs()


if __name__ == "__main__":
    main()
