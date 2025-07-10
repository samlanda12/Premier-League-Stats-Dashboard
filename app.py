from flask import Flask
from main import main_bp
from classes import League

app = Flask(__name__)

# load league object using sqlite-backed lazy access
league = League("data/prem_stats.db")

app.config['LEAGUE'] = league  # store league instance in app config

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)