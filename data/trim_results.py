#one-time script to trim csv
import pandas as pd
from analytics.data_load import clean_team_names

df = pd.read_csv('data/results.csv')

# cleaning similar to data_load.py pipeline
df['home'] = df['home'].str.strip().str.lower()
df['away'] = df['away'].str.strip().str.lower()

df = clean_team_names(df, 'home')
df = clean_team_names(df, 'away')

df['game'] = df['home'] + ' vs. ' + df['away']
df['date'] = df['date'].str.strip()
df['gameid'] = df['game'] + df['date']

df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
df = df[df['date_dt'].dt.year >= 1985]
df = df[(df['home_country'] == 'england') & (df['away_country'] == 'england')]

df_trimmed = df[['home', 'away', 'date', 'gh', 'ga', 'full_time', 'competition', 'gameid']].copy()

df_trimmed.to_csv('data/results_trimmed.csv', index=False)