from flask import Flask, render_template, request
from analysis import load_data
from visualize import visualize
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    # right now, you're loading all data on every load of the app - that's inefficient. Look into flask blueprint classes and make it do the data load once, on flask app initialization load.
    # it will then cache this data in memory and you'll write a separate endpoint to control reload of it if needed to refresh the cache
    gs = load_data() #load the data

    season_options = sorted(gs['season'].dropna().unique())
    club_options = sorted(set(gs['home_team'].dropna()) | set(gs['away_team'].dropna())) #generate dropdown options

    #initialize variables
    message = None
    plot_filename = None
    plot_url = None
    stats_summary = None
    club = None
    season = None

    if request.method == 'POST':
        #get selected club and season
        club = request.form.get('club', '').strip().lower()
        season = request.form.get('season', '').strip()

        #filter datasets to chosen items
        season_df = gs[gs['season'] == season]
        club_df = season_df[(season_df['home_team'] == club) | (season_df['away_team'] == club)].copy()

        #clean team
        if 'scoring_team' in club_df.columns:
            club_df['scoring_team'] = club_df['scoring_team'].str.strip().str.lower()

        if club_df.empty:
            message = f"No data available for {club.title()} in season {season}." #error handling
            plot_url = None # dont show image
            stats_summary = None
        else:
            plt.figure(figsize=(20, 18))
            visualize(club_df, club, season) #generate viz image
            
            #save viz image to plots folder
            plot_filename = 'static/plots/club_plot.png'
            plt.savefig(plot_filename)
            plt.close()
            plot_url = plot_filename

            # stat summary variables
            total_goals_scored = int(club_df[club_df['scoring_team'] == club]['gh'].sum() + club_df[club_df['scoring_team'] == club]['ga'].sum())
            wins = (club_df['winner'] == club).sum()
            draws = (club_df['winner'] == 'Draw').sum()
            losses = len(club_df) - wins - draws

            stats_summary = {
                'Total Goals Scored': total_goals_scored,
                'Wins': wins,
                'Draws': draws,
                'Losses': losses}
        # you're repeating a lot of code here, try to find a way to do this without doing so :)
        
        return render_template(
            'index.html',
            season_options = season_options,
            club_options = club_options,
            plot_url = plot_url,
            message = message,
            stats_summary = stats_summary,
            club = club,
            season = season)
    
    return render_template(
        'index.html',
        season_options = season_options,
        club_options = club_options,
        plot_url = None,
        message = None,
        stats_summary = None,
        club = club,
        season = season)

if __name__ == '__main__':
    app.run(debug=True)
