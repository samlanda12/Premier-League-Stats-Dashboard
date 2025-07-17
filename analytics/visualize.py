import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for flask
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np

def visualize(club_df, club, season, player_df=None, all_players=None):
    plt.figure(figsize=(20, 18))  # make dashboard for multiple viz

    plt.subplot(3, 2, 1)  # market value over seasons for the club
    if all_players is not None and all(col in all_players.columns for col in ['Season', 'Club', 'Market Value (€)']):
        # data is already normalized in ETL step
        club_mv = all_players[all_players['Club'] == club]  # filter by club
        if not club_mv.empty:
            club_mv = club_mv.groupby('Season')['Market Value (€)'].mean().reset_index()  # average value per season
            club_mv = club_mv.sort_values('Season')  # sort for lineplot
            club_mv['Season'] = pd.to_numeric(club_mv['Season'], errors='coerce')
            season_start = int(str(season).split('-')[0])  # extract start year as int
            if season_start in club_mv['Season'].values:
                sns.lineplot(data=club_mv, x='Season', y='Market Value (€)', marker='o')  # plot market value line
                plt.axvline(x=season_start, color='red', linestyle='--')  # mark selected season
                plt.title(f"Avg Market Value Over Time for {club.title()}")
                plt.xlabel("Season")
                plt.ylabel("Avg Market Value (10M€)")
            else:
                plt.title("No Market Value Data for Selected Season")
                plt.axis('off')  # hide chart if season missing
        else:
            plt.title("Market Value Data Not Available")
            plt.axis('off')  # hide chart if club has no data
    else:
        plt.title("Market Value Over Time (Data Unavailable)")
        plt.axis('off')  # hide chart if dataset missing

    plt.subplot(3, 2, 2)  # make second viz
    if club_df.empty or 'winner' not in club_df.columns:
        plt.title("No match results data available")
        plt.axis('off')
    else:
        results_df = pd.DataFrame({
            'Result': club_df['winner'].map(lambda x: 'Win' if x == club else 'Draw' if x == 'Draw' else 'Loss')
        })
        colors = {'Win': 'green', 'Draw': 'gray', 'Loss': 'red'}
        if results_df.empty or results_df['Result'].isnull().all():
            plt.title("No match results data available")
            plt.axis('off')
        else:
            sns.countplot(data=results_df, x='Result', hue='Result', palette=colors, legend=False)
            plt.title(f'Match Results Distribution for {club.title()} in {season} Season')
            plt.xlabel("Match Outcome")
            plt.ylabel("Number of Matches")

    plt.subplot(3, 2, 3)  # make third viz
    if club_df.empty or 'home_team' not in club_df.columns or 'away_team' not in club_df.columns or 'gh' not in club_df.columns or 'ga' not in club_df.columns:
        plt.title("No goals data available")
        plt.axis('off')
    else:
        home_goals = club_df[club_df['home_team'] == club]['gh']
        away_goals = club_df[club_df['away_team'] == club]['ga']
        if home_goals.empty and away_goals.empty:
            plt.title("No goals data available")
            plt.axis('off')
        else:
            goals_data = pd.DataFrame({'Goals': pd.concat([home_goals, away_goals]),
                                       'Type': ['Home'] * len(home_goals) + ['Away'] * len(away_goals)})
            if goals_data.empty or goals_data['Goals'].isnull().all():
                plt.title("No goals data available")
                plt.axis('off')
            else:
                sns.boxplot(data=goals_data, x='Type', y='Goals', hue='Type')
                plt.title(f'Goals Distribution (Home vs Away) for {club.title()} in {season} Season')
                plt.xlabel("Match Location")
                plt.ylabel("Goals Scored")

    plt.subplot(3, 2, 4)  # make fourth viz
    if club_df.empty or 'gh' not in club_df.columns or 'ga' not in club_df.columns or 'home_team' not in club_df.columns or 'away_team' not in club_df.columns:
        plt.title("No goal difference data available")
        plt.axis('off')
    else:
        is_home = club_df['home_team'] == club
        #use np.where for correct broadcasting
        club_df['goal_difference'] = np.where(is_home, club_df['gh'] - club_df['ga'], club_df['ga'] - club_df['gh'])
        if club_df['goal_difference'].isnull().all():
            plt.title("No goal difference data available")
            plt.axis('off')
        else:
            sns.histplot(data=club_df, x='goal_difference', bins=8)
            plt.title(f"Goal Difference Distribution for {club.title()} in ({season}) Season")
            plt.xlabel("Goal Difference")
            plt.ylabel("Number of Matches")

    plt.subplot(3, 2, 5)  # make fifth viz
    if club_df.empty or 'time' not in club_df.columns:
        plt.title("No goal time data available")
        plt.axis('off')
    else:
        club_df['minute'] = pd.to_numeric(club_df['time'], errors='coerce')
        if club_df['minute'].dropna().empty:
            plt.title("No goal time data available")
            plt.axis('off')
        else:
            sns.histplot(club_df['minute'].dropna(), bins=range(0, 100, 5), kde=True, color='purple')
            plt.title(f"Goal Times for {club.title()} in ({season}) Season")
            plt.xlabel("Minute of Match")
            plt.ylabel("Number of Goals")

    plt.subplot(3, 2, 6)  # make sixth viz
    if club_df.empty or 'winner' not in club_df.columns or 'date_dt' not in club_df.columns:
        plt.title("No cumulative wins data available")
        plt.axis('off')
    else:
        club_df['won'] = club_df['winner'] == club
        club_df = club_df.sort_values('date_dt')
        club_df['cumulative_wins'] = club_df['won'].cumsum()
        if club_df['date_dt'].isnull().all() or club_df['cumulative_wins'].isnull().all():
            plt.title("No cumulative wins data available")
            plt.axis('off')
        else:
            sns.lineplot(data=club_df, x='date_dt', y='cumulative_wins', marker='o')
            plt.title(f"Cumulative Wins for {club.title()} in ({season}) Season")
            plt.xlabel("Match Date")
            plt.ylabel("Cumulative Wins")

def save_visualization(club_df, club, season, output_path, player_df=None, all_players=None):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)  # ensure static/plots/ exists
    plt.figure(figsize=(20, 18))
    visualize(club_df, club, season, player_df, all_players)
    plt.savefig(output_path)
    plt.close()

def save_player_visualization(player_df, club, club_df, season, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)  # ensure static/plots/ exists
    plt.figure(figsize=(24, 12))

    plt.subplot(2, 3, 1)  # plot player scoring breakdown as barplot, using top 10 values from scoring_player
    if club_df.empty or 'scoring_player' not in club_df.columns or 'scoring_team' not in club_df.columns:
        plt.title(f"No scorer data available for {club.title()} in ({season}) Season")
        plt.axis('off')
    else:
        club_df['scoring_team'] = club_df['scoring_team'].str.strip().str.lower()  # normalize
        club_goals = club_df[club_df['scoring_team'] == club]
        club_goals = club_goals[club_goals['scoring_player'].notna()]
        if club_goals.empty:
            plt.title(f"No scorer data found for {club.title()} in ({season}) Season")
            plt.axis('off')
        else:
            top_scorers = club_goals['scoring_player'].value_counts().index[:10]
            if len(top_scorers) == 0:
                plt.title(f"No scorer data found for {club.title()} in ({season}) Season")
                plt.axis('off')
            else:
                sns.countplot(
                    data=club_goals[club_goals['scoring_player'].isin(top_scorers)],
                    y='scoring_player',
                    order=top_scorers,
                    color='orange'
                )
                plt.title(f"Top Scorers for {club.title()} in ({season}) Season")
                plt.xlabel("Goals")
                plt.ylabel("Player")

    plt.subplot(2, 3, 2)  # plot age vs market value scatterplot
    if player_df.empty or 'Age' not in player_df.columns or 'Market Value (€)' not in player_df.columns or 'Position' not in player_df.columns:
        plt.title('No player age/market value data available')
        plt.axis('off')
    else:
        mv_scale = 1e7
        player_df['Market Value Scaled'] = player_df['Market Value (€)'] / mv_scale
        if player_df[['Age', 'Market Value Scaled']].dropna().empty:
            plt.title('No player age/market value data available')
            plt.axis('off')
        else:
            sns.scatterplot(data=player_df, x='Age', y='Market Value Scaled', hue='Position')
            plt.title('Age vs Market Value')
            plt.xlabel('Age')
            plt.ylabel('Market Value (10M€)')

    plt.subplot(2, 3, 3)  # plot market value distribution as histogram
    if player_df.empty or 'Market Value Scaled' not in player_df.columns:
        plt.title('No market value data available')
        plt.axis('off')
    else:
        if player_df['Market Value Scaled'].dropna().empty:
            plt.title('No market value data available')
            plt.axis('off')
        else:
            sns.histplot(player_df['Market Value Scaled'].dropna(), bins=20, color='green')
            plt.title('Market Value Distribution')
            plt.xlabel('Market Value (10M€)')
            plt.ylabel('Player Count')

    plt.subplot(2, 3, 4)  # plot top 5 market value players
    if player_df.empty or 'Market Value (€)' not in player_df.columns or 'Name' not in player_df.columns:
        plt.title('No top player value data available')
        plt.axis('off')
    else:
        top5 = (
            player_df.sort_values('Market Value (€)', ascending=False)
            .dropna(subset=['Market Value (€)'])
            .drop_duplicates('Name')
            .head(5)
        )
        top5['Market Value Scaled'] = top5['Market Value (€)'] / 1e7
        if top5.empty:
            plt.title('No top player value data available')
            plt.axis('off')
        else:
            sns.barplot(data=top5, x='Market Value Scaled', y='Name', orient='h')
            plt.title('Top 5 Most Valuable Players')
            plt.xlabel('Market Value (10M€)')
            plt.ylabel('Player')

    plt.subplot(2, 3, 5)  # plot age distribution as histogram
    if player_df.empty or 'Age' not in player_df.columns:
        plt.title('No age distribution data available')
        plt.axis('off')
    else:
        if player_df['Age'].dropna().empty:
            plt.title('No age distribution data available')
            plt.axis('off')
        else:
            sns.histplot(player_df['Age'].dropna(), bins=range(15, 45, 2), kde=True, color='skyblue')
            plt.title('Squad Age Distribution')
            plt.xlabel('Age')
            plt.ylabel('Player Count')

    plt.subplot(2, 3, 6)  # plot nationality breakdown as pie chart
    if player_df.empty or 'Nationality' not in player_df.columns:
        plt.title(f'No nationality data available for {season}')
        plt.axis('off')
    else:
        nationality_counts = player_df['Nationality'].value_counts().head(10)
        if nationality_counts.empty:
            plt.title(f'No nationality data available for {season}')
            plt.axis('off')
        else:
            nationality_counts.plot.pie(autopct='%1.1f%%', startangle=90)
            plt.title(f'Nationality Breakdown ({season})')
            plt.ylabel("")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def save_player_comparison_viz(compare_df_peak, compare_df_full, selected_players, output_path, gs):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 15))  # set figure size with 3 stacked rows

    # defensive: ensure 'Market Value (€)' exists in both dfs
    for df in [compare_df_peak, compare_df_full]:
        if 'Market Value (€)' not in df.columns:
            if 'MarketValue' in df.columns:
                df['Market Value (€)'] = df['MarketValue']
            elif 'Market Value' in df.columns:
                df['Market Value (€)'] = df['Market Value']
            else:
                df['Market Value (€)'] = np.nan

    # copy dataframes to avoid modifying originals
    compare_df_peak = compare_df_peak.copy()
    compare_df_full = compare_df_full.copy()

    # ensure correct formats
    for df in [compare_df_peak, compare_df_full]:
        df['Market Value (€)'] = pd.to_numeric(df['Market Value (€)'], errors='coerce')
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
        df['Club'] = df['Club'].str.title()

    # all-time win percentage calculation using results_trimmed.csv
    win_percents = []
    for _, row in compare_df_peak.iterrows():
        club_name = row['Club'].lower().strip()  # normalize for match
        club_games = gs[
            (gs['home_team'] == club_name) |
            (gs['away_team'] == club_name)
        ]
        if not club_games.empty:
            wins = (club_games['winner'] == club_name).sum()
            win_pct = round(100 * wins / len(club_games), 1)
        else:
            win_pct = '-'
        win_percents.append(win_pct)
    compare_df_peak['All-Time Win %'] = win_percents # attach win % to peak df

    # calculate total goals using eng-premier-league.csv scoring_player column
    try:
        epg = pd.read_csv("data/eng-premier-league.csv")
        goal_counts = epg['scoring_player'].value_counts()
        compare_df_peak['Goals'] = compare_df_peak['Name'].map(goal_counts).fillna(0).astype(int)
    except Exception as e:
        compare_df_peak['Goals'] = 'Unavailable'

    #peak mv barplot
    plt.subplot(3, 1, 1)
    ax1 = sns.barplot(data=compare_df_peak, x='Market Value (€)', y='Name', palette='viridis')
    plt.title("Peak Market Value Comparison")
    plt.xlabel("Market Value (in € Millions)")
    plt.ylabel("Player")

    # convert x-axis ticks from raw euros to millions
    xticks = ax1.get_xticks()
    ax1.set_xticklabels([f"{int(x / 1e6)}" for x in xticks])

    # add season annotation next to each bar
    for i, row in compare_df_peak.iterrows():
        ax1.text(row['Market Value (€)'] + 1e6, i, f"({row['Season']})", va='center', fontsize=9, color='black')

    #mv by age scatterplot
    plt.subplot(3, 1, 2)
    ax2 = sns.scatterplot(data=compare_df_full, x='Age', y='Market Value (€)', hue='Name', s=150)
    plt.title("Market Value by Age Over Career")
    plt.xlabel("Age")
    plt.ylabel("Market Value (in € Millions)")

    # convert y-axis ticks from euros to millions
    yticks = ax2.get_yticks()
    ax2.set_yticklabels([f"{int(y / 1e6)}" for y in yticks])
    plt.legend(title='Player')

    #player info table
    plt.subplot(3, 1, 3)
    # build summary table with relevant fields
    table_data = compare_df_peak[[
        'Name', 'Age', 'Position', 'Nationality', 'Season', 'Club', 'Goals', 'All-Time Win %'
    ]].set_index('Name')

    # convert cell contents to strings
    cell_text = [[str(v) for v in row] for row in table_data.values]

    plt.axis('off')  # hide axes for clean table
    table = plt.table(cellText=cell_text,
                      rowLabels=table_data.index,
                      colLabels=table_data.columns,
                      cellLoc='center',
                      loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.1, 2.0)  # adjust scale for readability
    plt.title('Player Info')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()