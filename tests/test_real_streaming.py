from pathlib import Path

import duckdb
import pandas as pd

from src.streaming.consumer import run_consumer
from src.streaming.producer import run_producer


def test_producer_consumer_flow_local(tmp_path: Path, monkeypatch) -> None:
    # 1. Setup mock directories
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    streaming_dir = tmp_path / "streaming"

    # 2. Write dummy transaction
    pd.DataFrame(
        [
            {
                "transaction_id": "uuid-t1",
                "customer_id": "uuid-c1",
                "account_id": "uuid-a1",
                "transaction_date": "2026-05-23",
                "channel": "PIX",
                "amount": 5000.0,
                "is_suspicious": True,
            }
        ]
    ).to_csv(raw_dir / "transactions.csv", index=False)

    # 3. Setup mock env
    fallback_file = streaming_dir / "suspicious_transactions_fallback.jsonl"
    monkeypatch.setattr("src.streaming.producer.RAW_DIR", raw_dir)
    monkeypatch.setattr("src.streaming.producer.FALLBACK_PATH", fallback_file)
    monkeypatch.setattr("src.streaming.consumer.FALLBACK_PATH", fallback_file)

    db_file = tmp_path / "warehouse.duckdb"
    monkeypatch.setenv("DB_TARGET", "duckdb")
    monkeypatch.setenv("DUCKDB_PATH", str(db_file))

    # 4. Run producer (should fallback to JSONL since Redpanda is not running)
    run_producer()
    assert fallback_file.exists()

    # 5. Run consumer (one-shot mode to read local file)
    run_consumer(one_shot=True)

    # 6. Check database results
    con = duckdb.connect(str(db_file))
    res = con.execute("SELECT * FROM raw.streaming_suspicious_summary").fetchall()
    assert len(res) == 1
    assert res[0][0] == "uuid-c1"
    assert res[0][1] == 1  # count
    assert res[0][2] == 5000.0  # amount
    con.close()
