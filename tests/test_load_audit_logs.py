from pathlib import Path

import duckdb

from src.python_ingestion.load_audit_logs import load_audit_logs


def test_load_audit_logs_creates_table_in_duckdb(tmp_path: Path, monkeypatch) -> None:
    # 1. Create a dummy audit log JSONL file
    audit_file = tmp_path / "copilot_audit.jsonl"
    audit_file.write_text(
        '{"timestamp": "2026-05-22T23:00:00Z", "status": "answered", "question": "test query", "citations": ["doc1.md"], "guarded_sql": "SELECT 1", "response": "Hello"}\n',
        encoding="utf-8",
    )

    # 2. Setup mock environment variables pointing to DuckDB target
    db_file = tmp_path / "warehouse.duckdb"
    monkeypatch.setenv("DB_TARGET", "duckdb")
    monkeypatch.setenv("DUCKDB_PATH", str(db_file))
    monkeypatch.setenv("AI_AUDIT_PATH", str(audit_file))

    # 3. Create schema and test table loading
    load_audit_logs()

    # 4. Assert database records exist
    con = duckdb.connect(str(db_file))
    res = con.execute("SELECT * FROM raw.ai_copilot_audit").fetchall()
    assert len(res) == 1
    assert res[0][1] == "answered"
    assert res[0][2] == "test query"
    assert res[0][3] == "doc1.md"
    assert res[0][4] == "SELECT 1"
    assert res[0][5] == "Hello"
    con.close()
