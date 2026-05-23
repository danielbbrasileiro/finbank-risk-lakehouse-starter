# Phase 2 Task Checklist

This checklist tracks the current Phase 2 implementation state for the FinBank Risk Lakehouse portfolio.

## Completed

- [x] Added a DuckDB local warehouse path through `DB_TARGET=duckdb`.
- [x] Added optional CVM funds extraction with deterministic offline sample data.
- [x] Added AI copilot audit loading into `raw.ai_copilot_audit`.
- [x] Added dbt staging and mart models for AI copilot audit records.
- [x] Added a local Qdrant-backed vector retrieval module with keyword retrieval fallback.
- [x] Added Gemini-assisted SQL drafting and self-correction behind non-demo, non-test execution.
- [x] Added local suspicious-transaction producer and consumer modules.
- [x] Added `make streaming-demo` to run the producer and one-shot consumer flow.
- [x] Added Streamlit dashboard tabs for credit risk, transaction monitoring, and AI governance.
- [x] Added tests for CVM extraction, audit loading, and local streaming fallback.
- [x] Fixed Ruff lint violations left by the Phase 2 changes.

## Verified In This Checkout

- [x] `rtk .venv/bin/python -m pytest tests -q`
- [x] `rtk .venv/bin/ruff check src dashboards tests --fix`
- [x] `rtk env AI_DEMO_MODE=1 .venv/bin/python -m src.ai_assistant.eval_runner --eval-file ai/evals/risk_copilot.yml`
- [x] `rtk env DB_TARGET=duckdb make load`
- [x] `rtk env DB_TARGET=duckdb make streaming-demo`

## Integration Finding

- `rtk env DB_TARGET=duckdb make dbt` produced `dbt/target/run_results.json` with 44 successful dbt results, but the Make process did not return cleanly because dbt remained stuck at `Flushing usage events`. The process was terminated after the successful dbt artifact was written, so this remains an operational cleanup item rather than a model failure.
- `rtk env DB_TARGET=duckdb .venv/bin/streamlit run dashboards/streamlit_app.py --server.headless true --server.port 8502` did not open a local HTTP port. A focused `import streamlit` probe remained in Streamlit protobuf imports until it was terminated, so dashboard browser validation is still pending.

## Pending Runtime Checks

- [ ] `DB_TARGET=duckdb make run-dashboard`
- [ ] Investigate the dbt CLI tracking flush hang so `make dbt` returns exit code 0 without manual termination.

## Notes

- `task.md` and `walkthrough.md` were referenced in the previous handoff but did not exist in the repository before this stabilization pass.
- Full Postgres and Redpanda checks still depend on local Docker runtime availability.
- Live Gemini vector retrieval and SQL self-correction require `GOOGLE_API_KEY` and are intentionally bypassed in tests and demo mode.
