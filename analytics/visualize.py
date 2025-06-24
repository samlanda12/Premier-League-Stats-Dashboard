import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for flask
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def visualize(club_df, club, season, player_df=None, all_players=None):
    plt.figure(figsize=(20, 18))  # make dashboard for multiple viz

    plt.subplot(3, 2, 1)  # market value over seasons for the club
    if all_players is not None:
        all_players['Season'] = all_players['Season'].astype(str).str.split('-').str[0]  # normalize season format to just start year
        all_players['Market Value (€)'] = pd.to_numeric(all_players['Market Value (€)'], errors='coerce')  # clean market value
        all_players['Club'] = all_players['Club'].str.lower()  # normalize club name
        club_mv = all_players[all_players['Club'] == club]  # filter by club
        if not club_mv.empty:
            club_mv = club_mv.groupby('Season')['Market Value (€)'].mean().reset_index()  # average value per season
            club_mv = club_mv.sort_values('Season')  # sort for lineplot

            season_start = str(season).split('-')[0]  # extract start year from selected season
            if season_start in club_mv['Season'].values:
                sns.lineplot(data=club_mv, x='Season', y='Market Value (€)', marker='o')  # plot market value line
                plt.axvline(x=season_start, color='red', linestyle='--')  # mark selected season
                plt.title(f"Avg Market Value Over Time for {club.title()}")
                plt.xlabel("Season")
                plt.ylabel("Avg Market Value (€)")
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
    results_df = pd.DataFrame({
        'Result': club_df['winner'].map(lambda x: 'Win' if x == club else 'Draw' if x == 'Draw' else 'Loss')
    })  # map winner column to W/D/L
    colors = {'Win': 'green', 'Draw': 'gray', 'Loss': 'red'}  # make dict for viz colors
    sns.countplot(data=results_df, x='Result', hue='Result', palette=colors, legend=False)  # plot result distribution and make color based on result
    plt.title(f'Match Results Distribution for {club.title()} in {season} Season')
    plt.xlabel("Match Outcome")
    plt.ylabel("Number of Matches")

    plt.subplot(3, 2, 3)  # make third viz
    home_goals = club_df[club_df['home_team'] == club]['gh']  # make home goals variable
    away_goals = club_df[club_df['away_team'] == club]['ga']  # make away goals variable
    goals_data = pd.DataFrame({'Goals': pd.concat([home_goals, away_goals]),
                               'Type': ['Home'] * len(home_goals) + ['Away'] * len(away_goals)})  # make df for each goal to be home or away
    sns.boxplot(data=goals_data, x='Type', y='Goals', hue='Type')  # plot goal distribution
    plt.title(f'Goals Distribution (Home vs Away) for {club.title()} in {season} Season')
    plt.xlabel("Match Location")
    plt.ylabel("Goals Scored")

    plt.subplot(3, 2, 4)  # make fourth viz
    club_df['goal_difference'] = club_df.apply(
        lambda x: x['gh'] - x['ga'] if x['home_team'] == club else x['ga'] - x['gh'],
        axis=1)  # make goal difference field
    sns.histplot(data=club_df, x='goal_difference', bins=8)  # plot goal difference distribution
    plt.title(f"Goal Difference Distribution for {club.title()} in ({season}) Season")
    plt.xlabel("Goal Difference")
    plt.ylabel("Number of Matches")

    plt.subplot(3, 2, 5)  # make fifth viz
    club_df['minute'] = pd.to_numeric(club_df['time'], errors='coerce')  # convert time field to numeric for histplot
    sns.histplot(club_df['minute'].dropna(), bins=range(0, 100, 5), kde=True, color='purple')  # plot goal time distribution
    plt.title(f"Goal Times for {club.title()} in ({season}) Season")
    plt.xlabel("Minute of Match")
    plt.ylabel("Number of Goals")

    plt.subplot(3, 2, 6)  # make sixth viz
    club_df['won'] = club_df['winner'] == club  # get club wins
    club_df = club_df.sort_values('date_dt')  # sort date of results
    club_df['cumulative_wins'] = club_df['won'].cumsum()  # get running total of wins throughout season
    sns.lineplot(data=club_df, x='date_dt', y='cumulative_wins', marker='o')  # plot cumulative wins across dates
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
    club_goals = club_df[club_df['scoring_team'] == club]
    top_scorers = club_goals['scoring_player'].value_counts().index[:10]
    if len(top_scorers) == 0:
        plt.title(f"No scorer data found for {club.title()} in ({season}) Season")
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
    player_df['Age'] = pd.to_numeric(player_df['Age'], errors='coerce')
    player_df['Market Value (€)'] = pd.to_numeric(player_df['Market Value (€)'], errors='coerce')
    sns.scatterplot(data=player_df, x='Age', y='Market Value (€)', hue='Position')
    plt.title('Age vs Market Value')
    plt.xlabel('Age')
    plt.ylabel('Market Value (10M€)')

    plt.subplot(2, 3, 3)  # plot market value distribution as histogram
    sns.histplot(player_df['Market Value (€)'].dropna(), bins=20, color='green')
    plt.title('Market Value Distribution')
    plt.xlabel('Market Value (10M€)')
    plt.ylabel('Player Count')

    top5 = player_df.nlargest(5, 'Market Value (€)')  # get top 5 players by market value
    plt.subplot(2, 3, 4)  # plot top 5 market value players
    sns.barplot(data=top5, x='Market Value (€)', y='Name', orient='h')
    plt.title('Top 5 Most Valuable Players')
    plt.xlabel('Market Value (10M€)')
    plt.ylabel('Player')

    plt.subplot(2, 3, 5)  # plot age distribution as histogram
    sns.histplot(player_df['Age'].dropna(), bins=range(15, 45, 2), kde=True, color='skyblue')
    plt.title('Squad Age Distribution')
    plt.xlabel('Age')
    plt.ylabel('Player Count')

    plt.subplot(2, 3, 6)  # plot nationality breakdown as pie chart
    nationality_counts = player_df['Nationality'].value_counts().head(10)
    nationality_counts.plot.pie(autopct='%1.1f%%', startangle=90)
    plt.title(f'Nationality Breakdown ({season})')
    plt.ylabel("")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()