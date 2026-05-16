from __future__ import annotations

import shutil
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path


def publish_bronze(
    *,
    raw_dir: Path = Path("data/raw"),
    bronze_dir: Path = Path("data/bronze"),
    batch_id: str | None = None,
) -> list[Path]:
    batch = batch_id or datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    target_dir = bronze_dir / f"batch_id={batch}"
    target_dir.mkdir(parents=True, exist_ok=True)

    published: list[Path] = []
    for source in sorted(raw_dir.glob("*.csv")):
        target = target_dir / source.name
        shutil.copy2(source, target)
        published.append(target)
    return published


def main() -> None:
    parser = ArgumentParser(description="Publish validated raw CSV files into a local bronze batch.")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--bronze-dir", default="data/bronze")
    parser.add_argument("--batch-id")
    args = parser.parse_args()

    published = publish_bronze(
        raw_dir=Path(args.raw_dir),
        bronze_dir=Path(args.bronze_dir),
        batch_id=args.batch_id,
    )
    for path in published:
        print(path)
    print(f"Published {len(published)} raw files to local bronze.")


if __name__ == "__main__":
    main()
