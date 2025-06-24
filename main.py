from flask import Blueprint, render_template, request, current_app
from analytics.visualize import save_visualization, save_player_visualization, save_player_comparison_viz
from analytics.stats import generate_stats_summary, filter_club_season
import difflib  # added for fuzzy name matching

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    gs = current_app.config['GS_DATA']
    players = current_app.config['PLAYER_DATA']

    season_options = sorted(gs['season'].dropna().unique())
    club_options = sorted(set(gs['home_team'].dropna()) | set(gs['away_team'].dropna()))

    message = None
    plot_url = None
    download_url = None
    stats_summary = None
    player_df = None
    player_table = None
    club = None
    season = None
    view_mode = 'team'
    player1 = None
    player2 = None

    if request.method == 'POST':
        view_mode = request.form.get('view_mode', 'team')

        if view_mode == 'compare':
            player1 = request.form.get('player1', '').strip()
            player2 = request.form.get('player2', '').strip()

            if player1 and player2:
                all_names = players['Name'].dropna().unique().tolist()
                match1 = difflib.get_close_matches(player1, all_names, n=1, cutoff=0.7) #fuzzy matching
                match2 = difflib.get_close_matches(player2, all_names, n=1, cutoff=0.7)

                if match1 and match2:
                    compare_df_full = players[players['Name'].isin([match1[0], match2[0]])].copy()
                    compare_df_peak = compare_df_full.sort_values('Market Value (€)', ascending=False).drop_duplicates('Name')

                    plot_filename = 'static/plots/player_compare.png'
                    save_player_comparison_viz(compare_df_peak, compare_df_full, [match1[0], match2[0]], plot_filename, gs)
                    plot_url = plot_filename
                    download_url = plot_filename
                    player1 = match1[0]
                    player2 = match2[0]
                else:
                    message = "One or both players not found. Please check spelling."
            else:
                message = "Please enter two player names to compare."

        else:
            club = request.form.get('club', '').strip().lower()
            season = request.form.get('season', '').strip().replace('–', '-').replace('/', '-')  # normalize season input

            if season == "all":
                club_df = gs[(gs['home_team'] == club) | (gs['away_team'] == club)]
                player_df = players[players['Club'] == club]
            else:
                season_start = season.split('-')[0]
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
                    download_url = plot_filename
            else:
                if club_df.empty:
                    message = f"No match data available for {club.title()} in season {season}."
                else:
                    plot_filename = 'static/plots/club_plot.png'
                    save_visualization(club_df, club, season, plot_filename, player_df=player_df, all_players=players)  # pass all_players
                    plot_url = plot_filename
                    download_url = plot_filename
                    stats_summary = generate_stats_summary(club_df, club)

    return render_template(
        'index.html',
        season_options=season_options,
        club_options=club_options,
        plot_url=plot_url,
        download_url=download_url,
        message=message,
        stats_summary=stats_summary,
        club=club,
        season=season,
        view_mode=view_mode,
        player_table=player_table,
        player1=player1,
        player2=player2
    )