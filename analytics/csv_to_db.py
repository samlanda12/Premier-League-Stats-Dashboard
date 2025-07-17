import pandas as pd
import sqlite3
from pathlib import Path
from analytics.data_clean import clean_team_names, TEAM_NAME_FIXES

Path("data").mkdir(parents=True, exist_ok=True) # ensure parent exists

#load raw CSVs
df = pd.read_csv('data/results_trimmed.csv')
gs = pd.read_csv('data/eng-premier-league.csv')
players = pd.read_csv('data/player_data_prem.csv')

#clean 'game' field for home/away
teams = gs['game'].str.split('vs.', expand=True)
gs['home_team'] = teams[0].str.strip().str.lower()
away_with_score = teams[1].str.strip().str.lower()

away_split = away_with_score.str.split()
sliced_away = away_split.str.slice(0, -1)
gs['away_team'] = sliced_away.str.join(' ')

#team name cleaning
gs = clean_team_names(gs, 'home_team')
gs = clean_team_names(gs, 'away_team')
gs = clean_team_names(gs, 'scoring_team')

gs['home_team'] = gs['home_team'].replace(TEAM_NAME_FIXES)
gs['away_team'] = gs['away_team'].replace(TEAM_NAME_FIXES)

#unique game ID
gs['game'] = gs['home_team'] + ' vs. ' + gs['away_team']
gs['date'] = gs['date'].str.strip()
gs['gameid'] = gs['game'] + gs['date']

#clean df
df['home'] = df['home'].str.strip().str.lower()
df['away'] = df['away'].str.strip().str.lower()
df = clean_team_names(df, 'home')
df = clean_team_names(df, 'away')

df['game'] = df['home'] + ' vs. ' + df['away']
df['date'] = df['date'].str.strip()
df['gameid'] = df['game'] + df['date']

#date filtering
gs['date_dt'] = pd.to_datetime(gs['date'], errors='coerce')
df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')

gs = gs[gs['date_dt'].dt.year.between(1990, 2023)]
df = df[df['date_dt'].dt.year.between(1990, 2023)]

#ensure 'gh' and 'ga' columns exist in df before merge
def ensure_columns(df, columns):
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df

df = ensure_columns(df, ['gh', 'ga'])

#merge goals
gs = gs.drop(columns=['GH', 'GA'], errors='ignore')
merge_df = pd.DataFrame(df[['gameid', 'gh', 'ga']])
gs = gs.merge(merge_df, on='gameid', how='left')

#winner column
gs['winner'] = gs['home_team']
gs.loc[gs['gh'] < gs['ga'], 'winner'] = gs['away_team']
gs.loc[gs['gh'] == gs['ga'], 'winner'] = 'Draw'

#normalize player data for club and season format matching
players['Club'] = players['Club'].str.lower().str.strip()  # ensure lowercase club name
players['Season'] = players['Season'].astype(str).str.strip().str.replace('–', '-').str.replace('/', '-')  # normalize season format like '2023–2024' to '2023-2024'
players['Season'] = players['Season'].str.split('-').str[0]  # keep only the start year for season
players['Age'] = pd.to_numeric(players['Age'], errors='coerce')  # convert age to numeric
players['Market Value (€)'] = pd.to_numeric(players['Market Value (€)'], errors='coerce')  # convert market value to numeric

#save each cleaned df as a sql table
conn = sqlite3.connect('data/prem_stats.db')
gs.to_sql('goals', conn, index=False, if_exists='replace')
players.to_sql('players', conn, index=False, if_exists='replace')
df.to_sql('results', conn, index=False, if_exists='replace')
conn.close()