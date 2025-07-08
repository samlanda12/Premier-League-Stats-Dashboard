import pandas as pd
import sqlite3
from pathlib import Path

Path("data").mkdir(parents=True, exist_ok=True) #ensure parent exists

conn = sqlite3.connect('data/prem_stats.db')

#load and save each CSV as a SQL table
pd.read_csv('data/results_trimmed.csv').to_sql('results', conn, index=False, if_exists='replace')
pd.read_csv('data/eng-premier-league.csv').to_sql('goals', conn, index=False, if_exists='replace')
pd.read_csv('data/player_data_prem.csv').to_sql('players', conn, index=False, if_exists='replace')

conn.close()