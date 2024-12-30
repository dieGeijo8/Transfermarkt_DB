import mysql.connector
from mysql.connector import Error
import os
import logging

# mysql connection
host = os.getenv('HOST')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
database = os.getenv('DATABASE')

# configure logging
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, 'execution.log')

logging.basicConfig(
    filename=log_file,  # file path
    level=logging.INFO,  # INFO logging level - used for INFO and ERROR
    format='%(asctime)s - %(levelname)s - %(message)s'  # log message format
)

try:
    # Connect to the database
    connection = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database=database
    )

    if connection.is_connected():
        cursor = connection.cursor()
except Exception as e:
    logging.error(f"Error in the connection with the DB: {e}")

try:
    # Start a transaction - either all tables are created or no table is created
    connection.start_transaction()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS teams_table (
        Team_ID INT NOT NULL,
        Team_name VARCHAR(255) NOT NULL,
        PRIMARY KEY (Team_ID)
    );
    """

    cursor.execute(create_table_query)
    logging.info("Table 'teams_table' created successfully.")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS transfers_table (
        Player_ID INT NOT NULL,
        Player_Name VARCHAR(255) NOT NULL,
        Acquiring_team_ID INT NOT NULL,
        Acquiring_team_name VARCHAR(255) NOT NULL,
        Selling_team_ID INT NOT NULL,
        Selling_team_name VARCHAR(255) NOT NULL,
        Price BIGINT NOT NULL,
        Description TEXT,
        PRIMARY KEY (Player_ID, Acquiring_team_ID, Selling_team_ID)
    );
    """

    cursor.execute(create_table_query)
    logging.info("Table 'transfers_table' created successfully.")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS players_table (
        Team_ID INT NOT NULL,
        Player_ID INT NOT NULL,
        Player_name VARCHAR(255) NOT NULL,
        PRIMARY KEY (Player_ID, Team_ID)
    );
    """
    cursor.execute(create_table_query)
    logging.info("Table 'players_table' created successfully.")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS market_values_table (
        Team_ID INT NOT NULL,
        Team_name VARCHAR(255) NOT NULL,
        Player_ID INT NOT NULL,
        Player_name VARCHAR(255) NOT NULL,
        Market_value INT,
        PRIMARY KEY (Player_ID, Team_ID)
    );
    """
    cursor.execute(create_table_query)
    logging.info("Table 'market_values_table' created successfully.")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS injuries_table (
        Player_ID INT NOT NULL,
        Player_name VARCHAR(255),
        Injury VARCHAR(255),
        Start_date DATE,
        End_date DATE,
        Games_missed INT,
        Team_ID INT NOT NULL,
        PRIMARY KEY (Player_ID, Start_date, End_date)
    );
    """
    cursor.execute(create_table_query)
    logging.info("Table 'injuries table' created successfully.")

    # Commit the transaction
    connection.commit()
    logging.info("All tables created successfully, transaction committed.")
except Error as e:
    connection.rollback()
    logging.error(f"Error creating tables in the DB, transaction rolled back: {e}")

