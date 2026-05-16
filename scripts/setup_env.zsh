#!/bin/zsh
set -e

echo "Creating Python virtual environment..."
uv venv --allow-existing .venv
source .venv/bin/activate

echo "Installing dependencies..."
uv pip install -r requirements.txt

echo "Copying .env.example to .env if missing..."
if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "Environment ready."
