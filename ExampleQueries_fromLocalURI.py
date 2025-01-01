from sqlalchemy import create_engine, text
import pandas as pd
import os

host = 'localhost'
username = 'root'
password = 'Sopas_de_aj8!'
database = 'Mira_Transfermarkt'

DATABASE_URI = "mysql+pymysql://{}:{}@{}:3306/{}".format(username, password, host, database)
engine = create_engine(DATABASE_URI)

with engine.connect() as connection:
    tables = ['teams_table', 'players_table', 'market_values_table', 'transfers_table', 'injuries_table']
    for table in tables:
        result = connection.execute(text(f"SELECT * FROM {database}.{table} LIMIT 10;"))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        print(df)