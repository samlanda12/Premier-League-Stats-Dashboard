from flask import Blueprint, render_template, request, current_app
from analytics.visualize import save_visualization
from analytics.stats import generate_stats_summary, filter_club_season

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    gs = current_app.config['GS_DATA']

    season_options = sorted(gs['season'].dropna().unique())
    club_options = sorted(set(gs['home_team'].dropna()) | set(gs['away_team'].dropna()))

    message = None
    plot_url = None
    stats_summary = None
    club = None
    season = None

    if request.method == 'POST':
        club = request.form.get('club', '').strip().lower()
        season = request.form.get('season', '').strip()

        club_df = filter_club_season(gs, club, season)

        if club_df.empty:
            message = f"No data available for {club.title()} in season {season}."
        else:
            plot_filename = 'static/plots/club_plot.png'
            save_visualization(club_df, club, season, plot_filename)
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