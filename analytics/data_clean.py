TEAM_NAME_FIXES = {
    'brighton & hove albion': 'brighton hove albion',
    'wimbledon': 'afc wimbledon'
}

def clean_team_names(df, team_column):
    split = df[team_column].str.split()
    take_fc = split.str[-1].str.lower() == 'fc'
    split[take_fc] = split[take_fc].str.slice(0, -1)
    df[team_column] = split.str.join(' ')
    return df