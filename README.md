# Mira_Transfermarkt_WSL

This project has been developed using the Windows Subsystem for Linux (WSL).  
To run this project, ensure that MySQL is installed on your system.  

The `execution_etl.sh` Bash script will:  
1. Set up the required virtual environment and install dependencies.  
2. Execute three Python scripts to:
   - Create a MySQL database with five tables.
   - Populate these tables with data scraped from Transfermarkt.  

## Steps to Run the Bash Script

### 1. Set System Variables  
   Open the script and define the system variables required to connect to MySQL:  
   - `host`: MySQL host (e.g., `localhost`).  
   - `username`: MySQL username.  
   - `password`: MySQL password.  
   - `database`: Name of the MySQL database to be created.  

### 2. Execute the Script  
   Run the following command from the terminal or command prompt:  
   ```bash
   bash execution_etl.sh
   ```

### 3. Check execution logs 
After the script completes, review the log file located at `ETL_scripts/execution.log`
. This file provides detailed information about the execution of the Python scripts.

## Verify Data in the Tables
To verify that data has been successfully inserted into all five tables, 
run the following command from the terminal:   
   ```bash
   python ExampleQueries_fromLocalURI.py
   ``` 
This script will print the first 10 rows from each table to the console.