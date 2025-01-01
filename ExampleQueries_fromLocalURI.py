from sqlalchemy import create_engine, text
import pandas as pd

DATABASE_URI = "mysql+pymysql://root:Sopas_de_aj8!@localhost:3306/Mira_Transfermarkt"
engine = create_engine(DATABASE_URI)

with engine.connect() as connection:
    tables = ['teams_table', 'players_table', 'market_values_table', 'transfers_table', 'injuries_table']
    for table in tables:
        result = connection.execute(text(f"SELECT * FROM Mira_Transfermarkt.{table} LIMIT 10;"))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        print(df)