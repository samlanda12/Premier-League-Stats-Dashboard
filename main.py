from flask import Blueprint, render_template, request, current_app
from analytics.visualize import save_visualization, save_player_visualization
from analytics.stats import generate_stats_summary, filter_club_season

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    gs = current_app.config['GS_DATA']
    players = current_app.config['PLAYER_DATA']

    season_options = sorted(gs['season'].dropna().unique())
    club_options = sorted(set(gs['home_team'].dropna()) | set(gs['away_team'].dropna()))

    message = None
    plot_url = None
    stats_summary = None
    player_df = None
    player_table = None
    club = None
    season = None
    view_mode = 'team'

    if request.method == 'POST':
        club = request.form.get('club', '').strip().lower()
        season = request.form.get('season', '').strip().replace('–', '-').replace('/', '-')  # normalize form input for season
        season_start = season.split('-')[0]  # extract just the start year for player matching
        view_mode = request.form.get('view_mode', 'team')

        club_df = filter_club_season(gs, club, season)
        player_df = players[(players['Club'] == club) & (players['Season'] == season_start)]

        if not player_df.empty:
            player_table = player_df.to_dict(orient='records')  # prepare player table for rendering

        if view_mode == 'player':
            if player_df.empty:
                message = f"No player data available for {club.title()} in season {season}."
            else:
                plot_filename = 'static/plots/player_plot.png'
                save_player_visualization(player_df, club, club_df, season, plot_filename)
                plot_url = plot_filename
        else:
            if club_df.empty:
                message = f"No match data available for {club.title()} in season {season}."
            else:
                plot_filename = 'static/plots/club_plot.png'
                save_visualization(club_df, club, season, plot_filename, player_df=player_df, all_players=players)  # pass all_players
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
        season=season,
        view_mode=view_mode,
        player_table=player_table
    )