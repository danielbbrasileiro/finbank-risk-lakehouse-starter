#!/bin/zsh
set -e

echo "Starting local infrastructure..."
docker compose up -d

echo "Generating synthetic data..."
python src/python_ingestion/synthetic_generator.py

echo "Loading data into PostgreSQL..."
python src/python_ingestion/load_to_postgres.py

echo "Running dbt build..."
cd dbt
dbt build --profiles-dir .
cd ..

echo "Local pipeline finished."
