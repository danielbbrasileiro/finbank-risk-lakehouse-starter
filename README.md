# FinBank Risk Lakehouse

End-to-end banking data engineering and AI engineering portfolio project inspired by the DataTalksClub Data Engineering Zoomcamp.

## Business problem

This project simulates a financial institution data platform that monitors:

- credit portfolio exposure;
- delinquency and days past due;
- synthetic banking transactions;
- macroeconomic indicators from Brazil;
- financial statement data from public sources;
- data quality and lineage;
- AI-assisted risk analysis.

The goal is to connect finance/accounting knowledge with modern data engineering practices.

## Target stack

| Area | Technology |
|---|---|
| Ingestion | Python |
| Data validation | Rust CLI |
| Local environment | Docker Compose |
| Lake simulation | MinIO |
| Local warehouse | PostgreSQL |
| Cloud data lake | AWS S3 |
| Cloud warehouse | Snowflake |
| Transformations | SQL + dbt |
| Distributed processing | Databricks / Spark |
| AI Engineering | RAG + SQL assistant |
| Automation | Linux/zsh scripts |

## Architecture

```text
Data Sources
  ├── BCB API
  ├── CVM public files
  ├── Synthetic customers, loans and transactions
  └── Optional market data
        │
        ▼
Python ingestion + Rust validation
        │
        ▼
Local raw files / MinIO / S3 Bronze
        │
        ▼
Databricks / Spark Silver and Gold
        │
        ▼
Snowflake / PostgreSQL warehouse
        │
        ▼
dbt staging, intermediate and marts
        │
        ▼
Dashboard + AI Risk Assistant
```

## First milestone: local MVP

The first version runs locally:

```text
Synthetic data → Rust validation → PostgreSQL raw tables → dbt marts → Streamlit dashboard
```

After the local MVP works, the same logic is migrated to AWS S3, Snowflake and Databricks.

## Quick start

### 1. Clone and enter the project

```zsh
git clone <your-repo-url>
cd finbank-risk-lakehouse
```

### 2. Create environment file

```zsh
cp .env.example .env
```

### 3. Start local infrastructure

```zsh
docker compose up -d
```

This starts:

- PostgreSQL;
- MinIO;
- Qdrant;
- Redpanda.

### 4. Create Python environment

```zsh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Generate synthetic data

```zsh
python src/python_ingestion/synthetic_generator.py
```

### 6. Load data into PostgreSQL

```zsh
python src/python_ingestion/load_to_postgres.py
```

### 7. Run dbt

```zsh
cd dbt
dbt deps
dbt build --profiles-dir .
```

## Project phases

### Phase 0 — Repository setup

- Create repo structure.
- Create Docker Compose.
- Create synthetic data generator.
- Add local PostgreSQL.
- Add first dbt models.

### Phase 1 — Banking synthetic data

Tables:

- customers;
- accounts;
- loans;
- transactions;
- payments.

Goal: create realistic financial datasets without using sensitive data.

### Phase 2 — Public financial data

Add:

- BCB macroeconomic indicators;
- CVM financial statements;
- optional OpenFIGI mapping.

Goal: connect internal banking portfolio to external financial/macro context.

### Phase 3 — dbt analytics engineering

Create:

- staging models;
- intermediate models;
- marts;
- data quality tests;
- documentation and lineage.

### Phase 4 — Rust validator

Create `finbank-validator` CLI to validate:

- schema;
- required columns;
- duplicate IDs;
- invalid dates;
- negative balances;
- future transactions.

### Phase 5 — AWS + Snowflake

Move local raw/curated layers to:

- S3;
- Snowflake raw/staging/marts;
- dbt connected to Snowflake.

### Phase 6 — Databricks

Use Spark to process larger files and build:

- Bronze;
- Silver;
- Gold;
- features for risk analytics.

### Phase 7 — AI Risk Assistant

Build an assistant that can answer questions over:

- dbt documentation;
- risk marts;
- data quality reports;
- financial reports.

## AI & Gemma 4 31b

The **AI Risk Assistant** in this project is powered by **Gemma 4 31b**, the latest state-of-the-art open model from Google.

- **Engine:** Google AI Studio API.
- **Model:** `gemma-4-31b`.
- **Optimization:** To handle the free tier limit of **15 RPM (Requests Per Minute)**, the assistant implements a robust retry logic and intelligent context window management.
- **Capabilities:** 
    - Natural language querying of the dbt semantic layer.
    - Automated credit risk commentary.
    - Answering questions about data lineage and quality tests.

## Portfolio message

This project demonstrates the ability to design and implement a finance-oriented data platform using Python, SQL, Rust, Docker, dbt, AWS, Snowflake, Databricks and AI Engineering.
