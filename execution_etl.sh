#!/bin/bash

# exit if a command exit with non-zero status
set -e

# define the project root, the project subdirectory containing the python scripts
# and the path of the requirements file
PROJECT_ROOT=$(dirname "$0")
SCRIPT_DIR="$PROJECT_ROOT/ETL_scripts"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

# define the system variables used by the scripts to connect to mysql
export HOST="localhost"
export USERNAME="root"
export PASSWORD="Sopas_de_aj8!"
export DATABASE="Mira_Transfermarkt_bis"

# create a virtual environment when it doesn't exist
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
else
    echo "Virtual environment already exists."
fi

# activate the virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# install dependencies from requirements.txt
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

echo "Virtual environment setup and dependencies installed successfully."

# run the python scripts
python "$SCRIPT_DIR/CreateDB.py"
python "$SCRIPT_DIR/CreateTables.py"
python "$SCRIPT_DIR/ETL.py"

# deactivate the virtual environment - uncomment if you don't want to run anything after this script
# deactivate
