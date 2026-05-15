.PHONY: up down install generate load dbt run-dashboard rust-build rust-validate

up:
	docker compose up -d

down:
	docker compose down

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

generate:
	python src/python_ingestion/synthetic_generator.py

load:
	python src/python_ingestion/load_to_postgres.py

dbt:
	cd dbt && dbt build --profiles-dir .

run-dashboard:
	streamlit run dashboards/streamlit_app.py

rust-build:
	cd src/rust_validator && cargo build --release

rust-validate:
	cd src/rust_validator && cargo run -- validate --input ../../data/raw/transactions.csv --schema ../../schemas/transactions_schema.json
