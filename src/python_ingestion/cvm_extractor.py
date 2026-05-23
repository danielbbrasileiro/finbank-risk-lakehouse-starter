from __future__ import annotations

import io
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path("data/raw")

OFFLINE_SAMPLE = [
    {
        "cnpj": "12.345.678/0001-90",
        "fund_name": "FINBANK RENDA FIXA CREDITO PRIVADO FI",
        "fund_type": "FI",
        "status": "EM FUNCIONAMENTO NORMAL",
        "class_type": "Renda Fixa",
        "net_worth": 150000000.00,
    },
    {
        "cnpj": "98.765.432/0001-10",
        "fund_name": "FINBANK MULTIMERCADO ESTRATEGICO FIM",
        "fund_type": "FI",
        "status": "EM FUNCIONAMENTO NORMAL",
        "class_type": "Multimercado",
        "net_worth": 85000000.00,
    },
    {
        "cnpj": "45.678.901/0001-22",
        "fund_name": "FINBANK ACESSO ACOES FIA",
        "fund_type": "FI",
        "status": "FASE DE CAPTACAO",
        "class_type": "Ações",
        "net_worth": 12000000.00,
    },
]


def fetch_cvm_funds() -> pd.DataFrame:
    # URL for CVM general fund register (cad_fie)
    url = "https://dados.cvm.gov.br/dados/FIE/CAD/DADOS/cad_fie.csv"
    response = requests.get(url, timeout=45)
    response.raise_for_status()
    # Read with latin1 encoding since CVM files are encoded in ISO-8859-1 (latin1)
    df = pd.read_csv(io.StringIO(response.text), sep=";", encoding="latin1")
    return df


def normalize_cvm_funds(frame: pd.DataFrame) -> pd.DataFrame:
    # Map CVM columns to normalized columns
    normalized = frame.copy()

    # Rename columns safely if they exist
    col_mapping = {
        "CNPJ_FUNDO": "cnpj",
        "DENOM_SOCIAL": "fund_name",
        "TP_FUNDO": "fund_type",
        "SITUACAO": "status",
        "CLASSE": "class_type",
        "VL_PATRIM_LIQ": "net_worth",
    }

    # Filter only available mapped columns
    to_rename = {k: v for k, v in col_mapping.items() if k in normalized.columns}
    normalized = normalized.rename(columns=to_rename)

    # Ensure all required columns exist in output
    for col in col_mapping.values():
        if col not in normalized.columns:
            normalized[col] = None

    # Keep only target columns and limit rows to avoid massive tables for local demo
    final_cols = ["cnpj", "fund_name", "fund_type", "status", "class_type", "net_worth"]
    return normalized[final_cols].head(1000)


def write_offline_cvm_sample(*, raw_dir: Path = RAW_DIR) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(OFFLINE_SAMPLE)
    output = raw_dir / "cvm_funds.csv"
    df.to_csv(output, index=False)
    return output


def write_cvm_funds(*, raw_dir: Path = RAW_DIR) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_frame = fetch_cvm_funds()
    df = normalize_cvm_funds(raw_frame)
    output = raw_dir / "cvm_funds.csv"
    df.to_csv(output, index=False)
    return output


def main() -> None:
    parser = ArgumentParser(description="Extract CVM fund register data for the FinBank demo.")
    parser.add_argument("--offline-sample", action="store_true", help="Write a deterministic local sample.")
    parser.add_argument("--raw-dir", default="data/raw")
    args = parser.parse_args()

    if args.offline_sample:
        output = write_offline_cvm_sample(raw_dir=Path(args.raw_dir))
    else:
        output = write_cvm_funds(raw_dir=Path(args.raw_dir))
    print(f"Saved CVM funds data: {output}")


if __name__ == "__main__":
    main()
