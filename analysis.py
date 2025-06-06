#%%
import pandas as pd

def load_data():
    df = pd.read_csv('data/results.csv')
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
    home_split = gs['home_team'].str.split()
    away_split = gs['away_team'].str.split()
    scoring_split = gs['scoring_team'].str.split()
    take_home_fc = home_split.str[-1] == 'fc'
    take_away_fc = away_split.str[-1] == 'fc'
    take_scoring_fc = scoring_split.str[-1] == 'FC'
    home_split[take_home_fc] = home_split[take_home_fc].str.slice(0, -1)
    away_split[take_away_fc] = away_split[take_away_fc].str.slice(0, -1)
    scoring_split[take_scoring_fc] = scoring_split[take_scoring_fc].str.slice(0, -1)
    gs['home_team'] = home_split.str.join(' ')
    gs['away_team'] = away_split.str.join(' ')
    gs['scoring_team'] = scoring_split.str.join(' ')

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
    home_split_df = df['home'].str.split()
    away_split_df = df['away'].str.split()
    take_home_fc_df = home_split_df.str[-1] == 'fc'
    take_away_fc_df = away_split_df.str[-1] == 'fc'
    home_split_df[take_home_fc_df] = home_split_df[take_home_fc_df].str.slice(0, -1)
    away_split_df[take_away_fc_df] = away_split_df[take_away_fc_df].str.slice(0, -1)
    df['home'] = home_split_df.str.join(' ')
    df['away'] = away_split_df.str.join(' ')

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

    def determine_winner(row): #function to extract match winner
        if row['gh'] > row['ga']:
            return row['home_team']
        elif row['gh'] < row['ga']:
            return row['away_team']
        else:
            return 'Draw'

    gs['winner'] = gs.apply(determine_winner, axis=1) #create winner field
    return gs
