#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Print each command before execution (optional for debugging)
set -x

# Define the project root and subdirectory containing the Python script
PROJECT_ROOT=$(dirname "$0")
SCRIPT_DIR="$PROJECT_ROOT/ETL_scripts"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

export HOST="localhost"
export USERNAME="root"
export PASSWORD="Sopas_de_aj8!"
export DATABASE="Mira_Transfermarkt"

# Step 1: Create a virtual environment
# if [ ! -d "$PROJECT_ROOT/.venv" ]; then
python3 -m venv "$PROJECT_ROOT/.venv"
# fi

# Step 2: Activate the virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Step 3: Install dependencies from requirements.txt
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# Step 4: Run the Python script from the subdirectory
python "$SCRIPT_DIR/CreateDB.py"
python "$SCRIPT_DIR/CreateTables.py"
python "$SCRIPT_DIR/ETL.py"

# Step 5: Deactivate the virtual environment
deactivate
