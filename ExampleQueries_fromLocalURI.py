from sqlalchemy import create_engine, text
import pandas as pd

DATABASE_URI = "mysql+pymysql://root:Sopas_de_aj8!@localhost:3306/Mira_Transfermarkt"
engine = create_engine(DATABASE_URI)

with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM Mira_Transfermarkt.market_values_table LIMIT 10;"))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    print(df)