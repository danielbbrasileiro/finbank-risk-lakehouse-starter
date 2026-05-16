# AI Engineering Log

## Purpose

This log documents how AI is used in the project in a way that is visible to recruiters and reviewable by engineers.

## Decisions

- Use AI as a governed analyst copilot, not as a generic chat UI.
- Keep an offline deterministic mode so the demo and CI work without API keys.
- Ground answers in local project artifacts: docs, dbt models and schemas.
- Add SQL guardrails before any generated SQL is considered executable.
- Evaluate fixed scenarios through `make ai-eval`.

## Accepted Patterns

- Ask AI to draft analytical SQL, then pass it through policy checks.
- Ask AI to summarize lineage or data quality from local docs.
- Use AI-assisted implementation with tests and human review before merging.

## Rejected Patterns

- No unrestricted SQL execution.
- No hidden dependency on paid LLM APIs for the public demo.
- No claims that cloud resources are running unless they were actually provisioned.
- No publishing of secrets or raw credentials.

## LinkedIn Narrative

Post 1: data engineering case

- Problem: banking risk monitoring.
- Stack: Python, Rust, dbt, Postgres, Dagster, AWS/Snowflake/Databricks blueprint.
- Signal: reproducible pipeline and data contracts.

Post 2: analytics engineering and quality

- dbt marts, tests, exposures and lineage.
- Rust validation before loading.
- CI and Makefile commands.

Post 3: governed AI

- Retrieval over trusted project metadata.
- Read-only SQL guardrails.
- Deterministic evals.
- Responsible AI framing for data platforms.
