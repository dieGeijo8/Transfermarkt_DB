import requests
import pandas as pd
from bs4 import BeautifulSoup
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

# set headers
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

# set entry point
entry_url = 'https://www.transfermarkt.it/serie-a/startseite/wettbewerb/IT1/saison_id/2023'

# teams table
try:
    pageTree = requests.get(entry_url, headers=headers)
    pageTree.raise_for_status()  # Check for HTTP request errors
    soup = BeautifulSoup(pageTree.content, 'html.parser')
    table = soup.find('table', class_='items')

    if table is None:
        raise ValueError("Teams table error: Could not find the expected table in the webpage.")

    a_tags = table.find_all('a')

    team_names = []
    teams_hrefs = []
    for a_tag in a_tags:
        href = a_tag.get('href')
        if href is not None:
            # Take only the href referring to a team page, by analyzing the structure
            if ('/kader/verein/' in href) & ('/saison_id/2023' in href):
                name = a_tag.get('title')
                if name not in team_names:
                    teams_hrefs.append(href)
                    team_names.append(name)

    # Check if teams are missing
    if len(teams_hrefs) != 20 or len(team_names) != 20:
        raise ValueError(f"Teams table error: Inconsistent data. Found {len(teams_hrefs)} teams and {len(team_names)} names.")

    # Create the DataFrame
    teams_table = pd.DataFrame({
        'Team_ID': [url.replace("/saison_id/2023", "").split("/")[-1] for url in teams_hrefs],
        'Team_href': teams_hrefs,
        'Team_name': team_names,
    })
except requests.exceptions.RequestException as e:
    logging.error(f"Teams table HTTP Error: {e}")
except ValueError as e:
    logging.error(e)
except Exception as e:
    logging.error(f"Teams table unexpected error: {e}")


# transfers table
try:
    players_data = []
    for team_ID, team_href, team_name in zip(teams_table['Team_ID'].tolist(), teams_table['Team_href'].tolist(), teams_table['Team_name'].tolist()):
        # obtain the url to access the transfers page
        tranfers_URL = 'https://www.transfermarkt.it' + team_href.replace('kader', 'transfers')
        pageTree = requests.get(tranfers_URL, headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        tables = soup.find_all('table', class_='items')

        for table, i_table in zip(tables, range(len(tables))):
            td_tags = table.find_all('td', class_='hauptlink')
            for td, i_tag in zip(td_tags, range(len(td_tags))):
                if td.a is not None:
                    if i_tag % 3 == 0: # player, collect the id as well
                        players_data.append(int(td.a.get('href').split('/spieler/')[-1]))
                        players_data.append(td.a.get_text(strip=True))
                        if i_table == 0:
                            players_data.append(int(team_ID))
                            players_data.append(team_name)
                    elif (i_tag - 1) % 3 == 0: # team, collect the id as well
                        players_data.append(int(td.a.get('href').replace("/saison_id/2023", "").split("/")[-1]))
                        players_data.append(td.a.get_text(strip=True))
                        if i_table == 1:
                            players_data.append(int(team_ID))
                            players_data.append(team_name)
                    else:
                        players_data.append(td.a.get_text(strip=True))
                else:
                  # case of retired football players, missing data
                  players_data.append(td.text)
                  players_data.append('-')
                  players_data.append('-')
                  players_data.append('-')

    if len(players_data) % 7 != 0:
        raise ValueError(f"Transfers table error: Inconsistent players data.")

    players_data = [players_data[i:i + 7] for i in range(0, len(players_data), 7)]
    transfers_table = pd.DataFrame(players_data, columns=['Player_ID', 'Player_Name', 'Acquiring_team_ID', 'Acquiring_team_name', 'Selling_team_ID', 'Selling_team_name', 'Price'])
except requests.exceptions.RequestException as e:
    logging.error(f"Transfers table HTTP Error: {e}")
except ValueError as e:
    logging.error(e)
except Exception as e:
    logging.error(f"Transfers table unexpected error: {e}")

# players_table and market values table
try:
    players_data = []
    players_data_2 = []
    players_hrefs = []
    for team_ID, team_href, team_name in zip(teams_table['Team_ID'].tolist(), teams_table['Team_href'].tolist(), teams_table['Team_name'].tolist()):
        pageTree = requests.get('https://www.transfermarkt.it' + team_href, headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        table = soup.find('table', class_='items')

        # td tags of hauptlink class - the text returns player name and respective value
        td_tags = table.find_all('td', class_='hauptlink')

        for td, i_tag in zip(td_tags, range(len(td_tags))):
            if td.a is not None:
                if i_tag % 2 == 0: # player
                    # a player might be present in more teams, collect its page just once
                    if href not in players_hrefs:
                      players_hrefs.append(td.a.get('href'))
                    players_data.append(team_ID)
                    players_data.append(int(td.a.get('href').split('/spieler/')[-1]))
                    players_data.append(td.a.get_text(strip=True))
                    players_data_2.append(team_ID)
                    players_data_2.append(int(td.a.get('href').split('/spieler/')[-1]))
                    players_data_2.append(td.a.get_text(strip=True))
                else: # market value
                    players_data.append(td.a.get_text(strip=True))
            else:
                players_data.append(td.text)

    if len(players_data_2) % 3 != 0:
        raise ValueError(f"Market values table error: Inconsistent players data 2.")
    else:
        players_data_2 = [players_data_2[i:i + 3] for i in range(0, len(players_data_2), 3)]
        players_table = pd.DataFrame(players_data_2, columns=['Team_ID', 'Player_ID', 'Player_Name'])

    if len(players_data) % 4 != 0:
        raise ValueError(f"Market values table error: Inconsistent players data.")
    else:
        players_data = [players_data[i:i + 4] for i in range(0, len(players_data), 4)]
        market_values_table = pd.DataFrame(players_data, columns=['Team_ID', 'Player_ID', 'Player_Name', 'Market_value'])

    if len(players_data) != len(players_hrefs):
        raise ValueError(f"Market values table error: Inconsistency between players data and players href.")
except requests.exceptions.RequestException as e:
    logging.error(f"Transfers table HTTP Error: {e}")
except ValueError as e:
    logging.error(e)
except Exception as e:
    logging.error(f"Transfers table unexpected error: {e}")

# injuries table
try:
    players_data = []
    # drop the [:15]-it's the one that takes longer
    for player_href in players_hrefs[:15]:
        pageTree = requests.get('https://www.transfermarkt.it' + player_href.replace('profil', 'verletzungen'),
                                headers=headers)
        soup = BeautifulSoup(pageTree.content, 'html.parser')
        table = soup.find('table', class_='items')

        # find tr tags of class odd and even - rows of injuries table
        if table is not None:
            tr_tags = table.find_all('tr', class_='odd') + table.find_all('tr', class_='even')
            injuries = []
            for tr in tr_tags:
                td_texts = [td.text.strip() for td in tr.find_all('td')]
                if td_texts[0] == '23/24':
                    injuries.append(td_texts)
                    a_tag = tr.find('a')  # Look for the <a> tag
                    if a_tag is not None and a_tag.get('href'):  # Check if <a> exists and has 'href'
                        href = a_tag.get('href')
                        team_id = href.split('/verein/')[1].split('/')[0]
                    else:
                        team_id = 0
            if len(injuries) != 0:
                for injury in injuries:
                    # add the player id and keep just some of the data about the injury
                    players_data.append(
                        [player_href.split('/spieler/')[-1]] + [injury[i] for i in [1, 2, 3, 5]] + [team_id])

    injuries_table = pd.DataFrame(players_data, columns=['Player_ID', 'Injury', 'Start_date', 'End_date', 'Games_missed', 'Team_ID'])
except requests.exceptions.RequestException as e:
    logging.error(f"Injuries table HTTP Error: {e}")
except Exception as e:
    logging.error(f"Injuries table unexpected error: {e}")

# data cleaning
def convert_to_int(value):
    value = value.replace("€", "").strip()
    try:
      if "mila" in value:
          return int(float(value.replace("mila", "").replace(",", ".")) * 1000)
      elif "mln" in value:
          return int(float(value.replace("mln", "").replace(",", ".")) * 1_000_000)
      else:
          return 0
    except:
      return 0

month_mapping = {
    "gen": "1",
    "feb": "2",
    "mar": "3",
    "apr": "4",
    "mag": "5",
    "giu": "6",
    "lug": "7",
    "ago": "8",
    "set": "9",
    "ott": "10",
    "nov": "11",
    "dic": "12"
}

def replace_month(date_str):
    day, month, year = date_str.split("/")
    return f"{day}/{month_mapping[month.lower()]}/{year}"

# teams table
try:
    teams_table = pd.DataFrame(teams_table[['Team_ID', 'Team_name']]).astype({
        "Team_ID": "int64",
        "Team_name": "string"
    })
except Exception as e:
    logging.error(f"Teams table data cleaning unexpected error: {e}")

# players table
try:
    players_table = pd.DataFrame(players_table[['Team_ID', 'Player_ID', 'Player_Name']]).astype({
        "Team_ID": "int64",
        "Player_ID": "int64",
        "Player_Name": "string"
    })
    players_table = players_table.rename(columns={"Player_Name": "Player_name"})
except Exception as e:
    logging.error(f"Players table data cleaning unexpected error: {e}")

# market values table
try:
    market_values_table['Team_ID'] = market_values_table['Team_ID'].astype("int64")
    market_values_table = pd.merge(market_values_table, teams_table, on='Team_ID', how='left')
    market_values_table = market_values_table[['Team_name', 'Team_ID', 'Player_ID', 'Player_Name', 'Market_value']]
    market_values_table['Market_value'] = market_values_table['Market_value'].apply(convert_to_int)
    market_values_table = market_values_table.rename(columns={"Player_Name": "Player_name"})
    market_values_table = pd.DataFrame(market_values_table).astype({
        "Team_ID": "int64",
        "Team_name": "string",
        "Player_ID": "int64",
        "Player_name": "string",
        "Market_value": "int64"
    })
    market_values_table = market_values_table[['Team_ID', 'Team_name', 'Player_ID', 'Player_name', 'Market_value']]
except Exception as e:
    logging.error(f"Market values table data cleaning unexpected error: {e}")

# transfers table
try:
    description_column = []
    for index, row in transfers_table.iterrows():
        if row['Price'][-1] != '€' and row['Price'] != '-':
            description_column.append(row['Price'])
        else:
            description_column.append('-')
    transfers_table["Acquiring_team_ID"] = pd.to_numeric(transfers_table["Acquiring_team_ID"], errors="coerce").fillna(
        0).astype(int)
    transfers_table["Selling_team_ID"] = pd.to_numeric(transfers_table["Selling_team_ID"], errors="coerce").fillna(
        0).astype(int)
    transfers_table['Description'] = description_column
    transfers_table['Price'] = transfers_table['Price'].apply(convert_to_int)

    transfers_table = pd.DataFrame(transfers_table).astype({
        "Player_ID": "int64",
        "Player_Name": "string",
        "Acquiring_team_ID": "int64",
        "Acquiring_team_name": "string",
        "Selling_team_ID": "int64",
        "Selling_team_name": "string",
        "Price": "int64",
        "Description": "string",
    })
except Exception as e:
    logging.error(f"Transfers table data cleaning unexpected error: {e}")

# injuries_table
try:
    injuries_table["Games_missed"] = pd.to_numeric(injuries_table["Games_missed"], errors="coerce").fillna(0).astype(int)
    injuries_table = pd.DataFrame(injuries_table).astype({
        "Player_ID": "int64",
        "Injury": "string",
        "Start_date": "string",
        "End_date": "string",
        "Games_missed": "int64",
        "Team_ID": "int64"
    })
    injuries_table['Start_date'] = pd.to_datetime(injuries_table['Start_date'].apply(replace_month), format="%d/%m/%Y")
    injuries_table['End_date'] = pd.to_datetime(injuries_table['End_date'].apply(replace_month), format="%d/%m/%Y")
    players_table_copy = players_table[['Player_ID', 'Player_name']]
    players_table_copy.drop_duplicates()
    injuries_table = pd.merge(injuries_table, players_table_copy, on='Player_ID', how='left')
    injuries_table = injuries_table[['Player_ID', 'Player_name', 'Injury', 'Start_date', 'End_date', 'Games_missed', 'Team_ID']]
except Exception as e:
    logging.error(f"Injuries table data cleaning unexpected error: {e}")


# write data into SQL DB
try:
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
    # Start a transaction - either data is written in all tables or no data is written
    connection.start_transaction()

    insert_query = """
    INSERT IGNORE INTO teams_table (Team_ID, Team_name)
    VALUES (%s, %s)
    """

    records = list(teams_table.itertuples(index=False, name=None))

    cursor.executemany(insert_query, records)
    connection.commit()

    logging.info(f"{cursor.rowcount} records inserted successfully in teams table.")

    insert_query = """
                INSERT IGNORE INTO transfers_table (
                    Player_ID, Player_Name, Acquiring_team_ID, Acquiring_team_name, 
                    Selling_team_ID, Selling_team_name, Price, Description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

    # drop primary key duplicates - could happen cause the transfer in Transfermarkt is registered in both acquiring and selling team page
    transfers_table = transfers_table.drop_duplicates(subset=['Player_ID', 'Acquiring_team_ID', 'Selling_team_ID'], keep='first')
    records = list(transfers_table.itertuples(index=False, name=None))

    cursor.executemany(insert_query, records)
    connection.commit()

    logging.info(f"{cursor.rowcount} records inserted successfully in transfers table.")

    insert_query = """
    INSERT IGNORE INTO players_table (Team_ID, Player_ID, Player_name)
    VALUES (%s, %s, %s)
    """

    data_to_insert = list(players_table.itertuples(index=False, name=None))

    cursor.executemany(insert_query, data_to_insert)
    connection.commit()

    logging.info(f"{cursor.rowcount} records inserted successfully in players table.")

    insert_query = """
    INSERT IGNORE INTO market_values_table (Team_ID, Team_name, Player_ID, Player_Name, Market_value)
    VALUES (%s, %s, %s, %s, %s)
    """

    data_to_insert = list(market_values_table.itertuples(index=False, name=None))

    cursor.executemany(insert_query, data_to_insert)
    connection.commit()

    logging.info(f"{cursor.rowcount} records inserted successfully in market values table.")

    insert_query = """
    INSERT IGNORE INTO injuries_table (Player_ID, Player_name, Injury, Start_date, End_date, Games_missed, Team_ID)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    data_to_insert = list(injuries_table.itertuples(index=False, name=None))

    cursor.executemany(insert_query, data_to_insert)
    connection.commit()

    logging.info(f"{cursor.rowcount} records inserted successfully in injuries table.")
    # Commit the transaction
    connection.commit()
    logging.info("All data inserted successfully, transaction committed.")

except Error as e:
    # Rollback the transaction in case of error
    connection.rollback()
    logging.error(f"Error writing data in the DB, transaction rolled back: {e}")
