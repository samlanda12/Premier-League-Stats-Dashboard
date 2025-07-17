import pandas as pd
import sqlite3

def load_data():
    import sqlite3
    import pandas as pd
    conn = sqlite3.connect('data/prem_stats.db')
    df = pd.read_sql('SELECT * FROM results', conn)
    gs = pd.read_sql('SELECT * FROM goals', conn)
    players = pd.read_sql('SELECT * FROM players', conn)
    conn.close()
    return gs, players, df