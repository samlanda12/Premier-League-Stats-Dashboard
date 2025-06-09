import pandas as pd
from analytics.data_clean import clean_team_names, TEAM_NAME_FIXES

def load_data():
    df = pd.read_csv('data/results_trimmed.csv')
    gs = pd.read_csv('data/eng-premier-league.csv')

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

    #merge goals
    gs = gs.drop(columns=['GH', 'GA'], errors='ignore')
    gs = gs.merge(df[['gameid', 'gh', 'ga']], on='gameid', how='left')

    #winner column
    gs['winner'] = gs['home_team']
    gs.loc[gs['gh'] < gs['ga'], 'winner'] = gs['away_team']
    gs.loc[gs['gh'] == gs['ga'], 'winner'] = 'Draw'

    return gs
