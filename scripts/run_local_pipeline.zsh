#!/bin/zsh
set -e

echo "Starting local infrastructure..."
docker compose up -d

echo "Generating synthetic data..."
make generate

echo "Validating raw files with Rust data contracts..."
make validate

echo "Publishing validated files to local bronze..."
make publish-bronze

echo "Loading data into PostgreSQL..."
make load

echo "Running dbt build..."
make dbt

echo "Local pipeline finished."
