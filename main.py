from flask import Blueprint, render_template, request, current_app
from analytics.visualize import save_visualization, save_player_visualization, save_player_comparison_viz
from analytics.stats import generate_stats_summary, filter_club_season
import pandas as pd
import difflib  # added for fuzzy name matching
from classes import League  # import League class

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    league = current_app.config['LEAGUE']

    #lazy load clubs for dropdown
    club_df = league.get_combined_match_df()
    club_options = sorted(set(club_df['home_team'].dropna()) | set(club_df['away_team'].dropna()))
    season_options = sorted(club_df['season'].dropna().unique())  # default fallback

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
                # lazy player access for matching
                with league._connect() as conn:
                    all_players = pd.read_sql("SELECT * FROM players", conn)
                all_names = all_players['Name'].dropna().unique().tolist()
                match1 = difflib.get_close_matches(player1, all_names, n=1, cutoff=0.7)
                match2 = difflib.get_close_matches(player2, all_names, n=1, cutoff=0.7)

                if match1 and match2:
                    compare_df_full = all_players[all_players['Name'].isin([match1[0], match2[0]])].copy()
                    compare_df_full = compare_df_full.copy()
                    compare_df_full['MarketValue'] = compare_df_full['Market Value (€)']
                    del compare_df_full['Market Value (€)']
                    compare_df_peak = compare_df_full.sort_values(by='MarketValue', ascending=False).drop_duplicates('Name')

                    plot_filename = 'static/plots/player_compare.png'
                    gs = league.get_combined_match_df()
                    save_player_comparison_viz(compare_df_peak, compare_df_full, [match1[0], match2[0]], plot_filename, gs)
                    plot_url = plot_filename
                    download_url = plot_filename
                    player1 = match1[0]
                    player2 = match2[0]
                else:
                    message = "One or both players not found. Please check spelling."
            else:
                message = "Please enter two player names to compare."

        elif view_mode == 'compare_team':
            club1 = request.form.get('club1', '').strip().lower()
            club2 = request.form.get('club2', '').strip().lower()
            season = request.form.get('season', '').strip().replace('–', '-').replace('/', '-')

            if season == "all":
                df1 = league.get_all_matches(club1)
                df2 = league.get_all_matches(club2)
                #helper to get all player data across all seasons as df
                pd1 = league.get_all_players_df(club1)
                pd2 = league.get_all_players_df(club2)
            else:
                df1 = league.get_season(club1, season).match_df
                df2 = league.get_season(club2, season).match_df
                pd1 = league.get_season(club1, season).get_squad_df()
                pd2 = league.get_season(club2, season).get_squad_df()

            with league._connect() as conn:
                all_players = pd.read_sql("SELECT * FROM players", conn)
            save_visualization(df1, club1, season, 'static/plots/club1_plot.png', player_df=pd1, all_players=all_players)
            save_visualization(df2, club2, season, 'static/plots/club2_plot.png', player_df=pd2, all_players=all_players)

            plot_url = ['static/plots/club1_plot.png', 'static/plots/club2_plot.png']
            download_url = plot_url
            stats_summary = {
                club1.title(): generate_stats_summary(df1, club1),
                club2.title(): generate_stats_summary(df2, club2)
            }
            club = [club1, club2]

        else:
            club = request.form.get('club', '').strip().lower()
            season = request.form.get('season', '').strip().replace('–', '-').replace('/', '-')

            #replace static list with valid season list for selected club
            if club:
                season_options = league.get_valid_seasons(club)

            if season == "all":
                #helper to get all match data across all seasons as df
                club_df = league.get_all_matches(club)
                #helper to get all players across all seasons for club
                player_df = league.get_all_players_df(club)
            else:
                club_df = league.get_season(club, season).match_df
                player_df = league.get_season(club, season).get_squad_df()

            if not player_df.empty:
                player_table = player_df.to_dict(orient='records')

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
                    with league._connect() as conn:
                        all_players = pd.read_sql("SELECT * FROM players", conn)
                    save_visualization(club_df, club, season, plot_filename, player_df=player_df, all_players=all_players)
                    plot_url = plot_filename
                    download_url = plot_filename
                    #compute and retrieve season summary for this club
                    stats_summary = league.get_season(club, season).get_summary()

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