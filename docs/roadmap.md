# Roadmap

## Sprint 1 - Professional local foundation

- [x] Generate synthetic banking data.
- [x] Validate raw files with Rust data contracts.
- [x] Add Python tests, Ruff and CI.
- [x] Add governed AI offline evals.
- [ ] Start Docker Compose and run the full warehouse/dbt path.

## Sprint 2 - Data quality and analytics engineering

- [x] Compile Rust validator.
- [x] Validate CSV schema for customers, accounts, transactions and loans.
- [x] Add dbt mart documentation and exposures.
- [x] Add dbt business tests.
- [ ] Generate and publish dbt docs screenshot.

## Sprint 3 - Public data

- [ ] Add BCB extractor.
- [ ] Add CVM extractor.
- [ ] Create macroeconomic staging tables.
- [ ] Join macro features to credit portfolio.

## Sprint 4 - Cloud architecture

- [x] Create AWS S3 bucket blueprint with Terraform.
- [x] Document Bronze/Silver/Gold cloud path.
- [x] Add Snowflake raw and mart DDL.
- [ ] Run Terraform validate on a machine with Terraform installed.

## Sprint 5 - Databricks

- [x] Create Databricks notebook.
- [ ] Read Bronze data.
- [ ] Create Silver data.
- [ ] Create Gold features.

## Sprint 6 - Governed AI Risk Copilot

- [x] Add docs/dbt/schema retrieval corpus.
- [x] Add risk marts metadata to dbt schema docs.
- [x] Create controlled SQL assistant with guardrails.
- [x] Add deterministic AI evals.
- [ ] Add audited question/SQL/response persistence.
