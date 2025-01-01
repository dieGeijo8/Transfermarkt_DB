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
export DATABASE="Mira_Transfermarkt"

# create a virtual environment, by default recreate each time, to avoid
# compatibility issues when running on different machines or locations
python3 -m venv "$PROJECT_ROOT/.venv"

# activate the virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# install dependencies from requirements.txt
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# run the python scripts
python "$SCRIPT_DIR/CreateDB.py"
python "$SCRIPT_DIR/CreateTables.py"
python "$SCRIPT_DIR/ETL.py"

# deactivate the virtual environment - uncomment if you don't want to run anything after this script
# deactivate
