from flask import Flask
from main import main_bp
from analytics.data_load import load_data

app = Flask(__name__)

gs_data = load_data()  # load data once at startup
app.config['GS_DATA'] = gs_data  #store data in app config

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)