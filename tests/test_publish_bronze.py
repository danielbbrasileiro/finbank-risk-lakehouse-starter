from pathlib import Path

from src.python_ingestion.publish_bronze import publish_bronze


def test_publish_bronze_copies_raw_files_into_batch_partition(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    raw_dir.mkdir()
    (raw_dir / "customers.csv").write_text("customer_id\n1\n", encoding="utf-8")
    (raw_dir / "loans.csv").write_text("loan_id\n10\n", encoding="utf-8")

    published = publish_bronze(raw_dir=raw_dir, bronze_dir=bronze_dir, batch_id="2026-05-16T00-00-00")

    assert published == [
        bronze_dir / "batch_id=2026-05-16T00-00-00" / "customers.csv",
        bronze_dir / "batch_id=2026-05-16T00-00-00" / "loans.csv",
    ]
    assert published[0].read_text(encoding="utf-8") == "customer_id\n1\n"
