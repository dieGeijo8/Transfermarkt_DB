import mysql.connector
from mysql.connector import Error
import logging
import os

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
    # connect to MySQL server
    connection = mysql.connector.connect(
        host=host,
        user=username,
        password=password
    )
    if connection.is_connected():
        logging.info("Connected to MySQL server")

        cursor = connection.cursor()

        # create the database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        logging.info(f"Database '{database}' created or already exists.")

except Error as e:
    logging.error(f"Error creating the Database: {e}")


