#%%
import pandas as pd

def load_data():
    df = pd.read_csv('data/results_trimmed.csv')
    gs = pd.read_csv('data/eng-premier-league.csv')

    #clean gs
    #split 'game' field into home_team and away
    teams = gs['game'].str.split('vs.', expand=True)
    gs['home_team'] = teams[0].str.strip().str.lower()
    away_with_score = teams[1].str.strip().str.lower()

    #take out scoreline the from away
    away_split = away_with_score.str.split()
    sliced_away = away_split.str.slice(0, -1)
    gs['away_team'] = sliced_away.str.join(' ')

    #take out 'fc' from home and away for better merge
    gs = clean_team_names(gs, 'home_team')
    gs = clean_team_names(gs, 'away_team')
    gs = clean_team_names(gs, 'scoring_team')

    #dictionary to match found mismatches
    team_name_fixes = {'brighton & hove albion': 'brighton hove albion', 'wimbledon': 'afc wimbledon'}
    gs['home_team'] = gs['home_team'].replace(team_name_fixes)
    gs['away_team'] = gs['away_team'].replace(team_name_fixes)

    #get unique game id
    gs['game'] = gs['home_team'] + ' vs. ' + gs['away_team']
    gs['date'] = gs['date'].str.strip()
    gs['gameid'] = gs['game'] + gs['date']

    #clean df
    #match home and away
    df['home'] = df['home'].str.strip().str.lower()
    df['away'] = df['away'].str.strip().str.lower()

    #take out fc for better merge
    df = clean_team_names(df, 'home')
    df = clean_team_names(df, 'away')

    #get unique game id
    df['game'] = df['home'] + ' vs. ' + df['away']
    df['date'] = df['date'].str.strip()
    df['gameid'] = df['game'] + df['date']

    #filter datasets to 1990-2023 (AI bot helped me with .dt.year.between)
    gs['date_dt'] = pd.to_datetime(gs['date'], errors='coerce')
    df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
    gs = gs[gs['date_dt'].dt.year.between(1990, 2023)]
    df = df[df['date_dt'].dt.year.between(1990, 2023)]

    gs = gs.drop(columns=['GH', 'GA'], errors='ignore') # remove old rows
    gs = gs.merge(df[['gameid', 'gh', 'ga']], on='gameid', how='left') #merge new rows

    gs['winner'] = gs['home_team']
    gs.loc[gs['gh'] < gs['ga'], 'winner'] = gs['away_team']
    gs.loc[gs['gh'] == gs['ga'], 'winner'] = 'Draw'

    return gs

def clean_team_names(df, team_column):
    split = df[team_column].str.split()
    take_fc = split.str[-1].str.lower() == 'fc'
    split[take_fc] = split[take_fc].str.slice(0, -1)
    df[team_column] = split.str.join(' ')
    return df

def generate_stats_summary(club_df, club):
    return {
        'Total Goals Scored': int(club_df[club_df['scoring_team'] == club]['gh'].sum() + club_df[club_df['scoring_team'] == club]['ga'].sum()),
        'Wins': (club_df['winner'] == club).sum(),
        'Draws': (club_df['winner'] == 'Draw').sum(),
        'Losses': len(club_df) - (club_df['winner'] == club).sum() - (club_df['winner'] == 'Draw').sum()
    }
