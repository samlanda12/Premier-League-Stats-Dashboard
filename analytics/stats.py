def filter_club_season(gs, club, season):
    season_df = gs[gs['season'] == season]
    club_df = season_df[(season_df['home_team'] == club) | (season_df['away_team'] == club)].copy()

    if 'scoring_team' in club_df.columns:
        club_df['scoring_team'] = club_df['scoring_team'].str.strip().str.lower()

    return club_df

def generate_stats_summary(club_df, club):
    club = club.strip().lower()
    home_goals = club_df[club_df['home_team'] == club]['gh'].sum()
    away_goals = club_df[club_df['away_team'] == club]['ga'].sum()
    return {
        'Total Goals Scored': int(home_goals + away_goals),
        'Wins': (club_df['winner'] == club).sum(),
        'Draws': (club_df['winner'] == 'Draw').sum(),
        'Losses': len(club_df) - (club_df['winner'] == club).sum() - (club_df['winner'] == 'Draw').sum()
    }