from __future__ import annotations

from pathlib import Path
import requests
import pandas as pd

RAW_DIR = Path("data/raw/bcb")
RAW_DIR.mkdir(parents=True, exist_ok=True)

SERIES = {
    "selic": 11,
    "credit_free_total": 20542,
}


def fetch_bcb_series(series_id: int, start_date: str, end_date: str) -> pd.DataFrame:
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados"
        f"?formato=json&dataInicial={start_date}&dataFinal={end_date}"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    df = pd.DataFrame(response.json())
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["series_id"] = series_id
    return df


def main() -> None:
    for name, series_id in SERIES.items():
        df = fetch_bcb_series(series_id, "01/01/2020", "31/12/2026")
        df.to_csv(RAW_DIR / f"{name}.csv", index=False)
        print(f"Saved {name}: {len(df):,} rows")


if __name__ == "__main__":
    main()
