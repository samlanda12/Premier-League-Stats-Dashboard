from flask import Blueprint, render_template, request, current_app
from analytics.visualize import visualize
from analytics.data_load import generate_stats_summary

import matplotlib.pyplot as plt

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    gs = current_app.config['GS_DATA']  #use cache data from the app config

    season_options = sorted(gs['season'].dropna().unique())
    club_options = sorted(set(gs['home_team'].dropna()) | set(gs['away_team'].dropna()))

    #initialize variables
    message = None
    plot_filename = None
    plot_url = None
    stats_summary = None
    club = None
    season = None

    if request.method == 'POST':
        club = request.form.get('club', '').strip().lower()
        season = request.form.get('season', '').strip()

        season_df = gs[gs['season'] == season]
        club_df = season_df[(season_df['home_team'] == club) | (season_df['away_team'] == club)].copy()

        if 'scoring_team' in club_df.columns:
            club_df['scoring_team'] = club_df['scoring_team'].str.strip().str.lower()

        if club_df.empty:
            message = f"No data available for {club.title()} in season {season}."
            plot_url = None
            stats_summary = None
        else:
            plt.figure(figsize=(20, 18))
            visualize(club_df, club, season)

            plot_filename = 'static/plots/club_plot.png'
            plt.savefig(plot_filename)
            plt.close()
            plot_url = plot_filename

            stats_summary = generate_stats_summary(club_df, club)

    return render_template(
        'index.html',
        season_options=season_options,
        club_options=club_options,
        plot_url=plot_url,
        message=message,
        stats_summary=stats_summary,
        club=club,
        season=season
    )