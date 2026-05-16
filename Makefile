.PHONY: up down install bootstrap generate publish-bronze load validate dbt pipeline test lint ai-eval dagster run-dashboard rust-build rust-validate demo

PYTHON ?= .venv/bin/python
DBT ?= .venv/bin/dbt
RUFF ?= .venv/bin/ruff
STREAMLIT ?= .venv/bin/streamlit
DAGSTER ?= .venv/bin/dagster

up:
	docker compose up -d

down:
	docker compose down

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

bootstrap:
	uv venv --allow-existing .venv
	uv pip install -r requirements.txt

generate:
	$(PYTHON) src/python_ingestion/synthetic_generator.py

publish-bronze:
	$(PYTHON) src/python_ingestion/publish_bronze.py

load:
	$(PYTHON) src/python_ingestion/load_to_postgres.py

validate: rust-build rust-validate

dbt:
	cd dbt && ../$(DBT) build --profiles-dir .

pipeline: generate validate publish-bronze load dbt

test:
	$(PYTHON) -m pytest tests -q

lint:
	$(RUFF) check src dashboards tests

ai-eval:
	$(PYTHON) -m src.ai_assistant.eval_runner --eval-file ai/evals/risk_copilot.yml

dagster:
	$(DAGSTER) dev -f orchestration/dagster_defs.py

demo: pipeline
	@echo "Pipeline ready. Run 'make run-dashboard' to open the Streamlit demo."

run-dashboard:
	$(STREAMLIT) run dashboards/streamlit_app.py

rust-build:
	cd src/rust_validator && cargo build --release

rust-validate:
	cd src/rust_validator && cargo run -- validate --input ../../data/raw/customers.csv --schema ../../schemas/customers_schema.json
	cd src/rust_validator && cargo run -- validate --input ../../data/raw/accounts.csv --schema ../../schemas/accounts_schema.json
	cd src/rust_validator && cargo run -- validate --input ../../data/raw/transactions.csv --schema ../../schemas/transactions_schema.json
	cd src/rust_validator && cargo run -- validate --input ../../data/raw/loans.csv --schema ../../schemas/loans_schema.json
