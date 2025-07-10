import pandas as pd
import sqlite3
from pathlib import Path
from data_load import load_data

Path("data").mkdir(parents=True, exist_ok=True) #ensure parent exists

conn = sqlite3.connect('data/prem_stats.db')

gs, players = load_data() #load cleaned data using existing pipeline

#save each cleaned df as a sql table
gs.to_sql('goals', conn, index=False, if_exists='replace')
players.to_sql('players', conn, index=False, if_exists='replace')

conn.close()