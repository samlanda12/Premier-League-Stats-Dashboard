from flask import Flask
from main import main_bp
from analytics.data_load import load_data
from classes import League

app = Flask(__name__)

gs_data, player_data = load_data()  # load data once at startup
app.config['GS_DATA'] = gs_data  #store data in app config
app.config['PLAYER_DATA'] = player_data

#load league object with paths to data files
league = League(
    match_data_path='data/results_trimmed.csv',
    goal_data_path='data/eng-premier-league.csv',
    player_data_path='data/player_data_prem.csv'
)
league.load()

app.config['LEAGUE'] = league  # store league instance in app config

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)