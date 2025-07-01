#!/bin/bash

# Print booting message
echo "Booting up"

# Check for .env file and load environment variables
if [ -f /app/.env ]; then
    echo "Loading environment variables from .env file"
    set -a
    . /app/.env
    set +a
else
    echo "No .env file found. Using default environment variables."
fi

# Check for virtual environment and activate it, or create a new one
if [ -f /app/venv/bin/activate ]; then
    source /app/venv/bin/activate
else
    echo "Virtual environment not found. Creating a new one."
    python3 -m venv /app/venv
    source /app/venv/bin/activate
    pip install -r /app/requirements.txt
fi

# Initialize database if it doesn't exist
if [ ! -f /app/data/users.db ]; then
    /app/xdnext init
fi

# Run the main script
/app/main.sh

# Keep the script running
tail -f /dev/null
