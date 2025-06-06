import seaborn as sns
import matplotlib
matplotlib.use('Agg') # non-interactive backend for flask
import matplotlib.pyplot as plt
import pandas as pd

def visualize(club_df, club, season):
    plt.figure(figsize=(20, 18))  # make dashboard for multiple viz

    plt.subplot(3, 2, 1)  # make first viz
    club_goals = club_df[club_df['scoring_team'] == club]  # filter for clubs goals
    top_scorers = club_goals['scoring_player'].value_counts().index[:10]  # get top scorers
    if len(top_scorers) == 0:
        plt.title(f"No scorer data found for {club.title()} in ({season}) Season")
    else:
        sns.countplot(data=club_goals[club_goals['scoring_player'].isin(top_scorers)], y='scoring_player',
                      order=top_scorers)  # plot top scorers in order
        plt.title(f"Top Scorers for {club.title()} in ({season}) Season")
        plt.xlabel("Number of Goals")
        plt.ylabel("Player")

    plt.subplot(3, 2, 2)  # make second viz
    results = []  # make lists for results
    for _, match in club_df.iterrows():
        if match['winner'] == club:
            results.append('Win')  # make win field
        elif match['winner'] == 'Draw':
            results.append('Draw')  # make draw field
        else:
            results.append('Loss')  # make loss field
    results_df = pd.DataFrame({'Result': results})  # make a results df
    colors = {'Win': 'green', 'Draw': 'gray', 'Loss': 'red'}  # make dict for viz colors
    sns.countplot(data=results_df, x='Result', hue='Result', palette=colors,
                  legend=False)  # plot result distribution and make color based on result
    plt.title(f'Match Results Distribution for {club.title()} in {season} Season')
    plt.xlabel("Match Outcome")
    plt.ylabel("Number of Matches")

    plt.subplot(3, 2, 3)  # make third viz
    home_goals = club_df[club_df['home_team'] == club]['gh']  # make home goals variable
    away_goals = club_df[club_df['away_team'] == club]['ga']  # make away goals variable
    goals_data = pd.DataFrame({'Goals': pd.concat([home_goals, away_goals]),
                               'Type': ['Home'] * len(home_goals) + ['Away'] * len(
                                   away_goals)})  # make df for each goal to be home or away
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
    sns.histplot(club_df['minute'].dropna(), bins=range(0, 100, 5), kde=True,
                 color='purple')  # plot goal time distribution
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