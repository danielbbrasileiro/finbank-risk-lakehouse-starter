# Phase 2 Technical Walkthrough

This walkthrough summarizes the Phase 2 implementation currently present in the repository. It is written as an engineering verification artifact, not a marketing summary.

## Scope

Phase 2 extends the original local banking-risk lakehouse with four practical capabilities:

1. Local DuckDB execution for demos that do not require Docker.
2. Governed AI copilot improvements, including audit persistence, optional vector retrieval, and SQL correction.
3. Suspicious-transaction streaming literacy through Redpanda when available and JSONL fallback when offline.
4. Streamlit dashboard views for transaction monitoring and AI governance.

## DuckDB Local Warehouse

`Makefile` now routes `make load` to DuckDB when `DB_TARGET=duckdb` or `DBT_TARGET=duckdb` is set. The loader in `src/python_ingestion/load_to_duckdb.py` creates `data/warehouse.duckdb`, loads core raw CSV files, and includes optional macro and CVM datasets when present.

The dbt profile in `dbt/profiles.yml` includes a `duckdb` target pointing at `../data/warehouse.duckdb` by default. This allows a cost-free local path for demo and recruiter review without requiring a running Postgres container.

## CVM Public Data

`src/python_ingestion/cvm_extractor.py` adds a CVM fund-register extractor. The production path reads the CVM CSV endpoint and normalizes the expected fields. The offline path writes a deterministic sample so the local pipeline remains reproducible without network access.

The Rust validator now conditionally validates `data/raw/cvm_funds.csv` when present using `schemas/cvm_funds_schema.json`.

## Governed AI Copilot

The original copilot remains deterministic in tests and demo mode. When `GOOGLE_API_KEY` is set and demo/test mode is disabled, `src/ai_assistant/governed_copilot.py` can:

- build a local retrieval corpus from docs, dbt models, and schemas;
- attempt semantic retrieval through Qdrant via `src/ai_assistant/vector_retrieval.py`;
- fall back to keyword retrieval if vector retrieval fails;
- ask Gemini to draft read-only SQL;
- pass generated SQL through existing guardrails before execution;
- execute against Postgres or local DuckDB;
- attempt up to two SQL self-correction passes if the warehouse returns an execution error;
- write auditable query records when `AI_AUDIT_PATH` is configured.

The audit loader in `src/python_ingestion/load_audit_logs.py` writes JSONL audit records into `raw.ai_copilot_audit`. dbt then exposes them through `stg_ai_copilot_audit` and `mart_ai_copilot_audit`.

## Streaming Demo

`src/streaming/producer.py` reads suspicious transactions from `data/raw/transactions.csv`. It attempts to send events to the `suspicious-transactions` Redpanda topic through the configured `KAFKA_BROKER`. If the broker is unavailable, it writes the same events to `data/streaming/suspicious_transactions_fallback.jsonl`.

`src/streaming/consumer.py` consumes from Redpanda when possible or from the JSONL fallback otherwise. It upserts customer-level metrics into `raw.streaming_suspicious_summary`:

- `customer_id`
- `suspicious_count`
- `total_suspicious_amount`
- `last_suspicious_timestamp`

`make streaming-demo` runs the producer and then the consumer in one-shot mode.

## Dashboard Changes

`dashboards/streamlit_app.py` now supports Postgres with DuckDB fallback and explicit DuckDB mode via `DB_TARGET=duckdb`.

The dashboard is organized into three tabs:

- Credit risk and exposure.
- Transaction monitoring.
- AI governance and operational audit.

The transaction-monitoring view reads batch marts and, when available, the streaming suspicious summary table populated by the local stream consumer.

## Verification Commands

Use these commands for the local no-Docker path:

```bash
AI_DEMO_MODE=1 make pipeline-local
DB_TARGET=duckdb make load
DB_TARGET=duckdb make dbt
DB_TARGET=duckdb make streaming-demo
DB_TARGET=duckdb make run-dashboard
```

Use these commands for engineering checks:

```bash
rtk .venv/bin/python -m pytest tests -q
rtk .venv/bin/ruff check src dashboards tests
AI_DEMO_MODE=1 make ai-eval
```

Observed in this checkout:

- Python tests: 30 passed.
- Ruff: all checks passed for `src`, `dashboards`, and `tests`.
- AI evals: 5/5 passed.
- DuckDB load: raw core, macro, and CVM tables loaded successfully.
- Streaming demo: Redpanda was unavailable, so the JSONL fallback path processed 15 suspicious events successfully.
- dbt DuckDB build: `dbt/target/run_results.json` recorded 44 successful results, but the Make process was manually terminated because dbt remained stuck at `Flushing usage events` after writing successful artifacts.
- Dashboard smoke: Streamlit did not open a local HTTP port in this environment; a focused `import streamlit` probe remained in Streamlit protobuf imports and was terminated.

## Known Boundaries

- Full Redpanda validation requires Docker and the broker service running.
- Live semantic retrieval and SQL self-correction require a valid `GOOGLE_API_KEY`.
- The current tests intentionally exercise the deterministic and local fallback paths so CI remains stable.
- The dbt tracking flush behavior should be investigated before treating `make dbt` as a clean local command, even though the model/test artifact recorded success.
- Dashboard browser validation remains pending until the Streamlit import/runtime hang is resolved.
