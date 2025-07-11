from analytics.stats import filter_club_season, generate_stats_summary
import pandas as pd
import sqlite3

class Player: #represents a single player from a club squad for a given season
    def __init__(self, name, position, age, nationality, market_value, season, club):
        self.name = name
        self.position = position
        self.age = age
        self.nationality = nationality
        self.market_value = market_value
        self.season = season
        self.club = club

    def to_dict(self): #converts the Player instance into a dictionary for dataframe/table use
        return {
            "Name": self.name,
            "Position": self.position,
            "Age": self.age,
            "Nationality": self.nationality,
            "Market Value (€)": self.market_value,
            "Season": self.season,
            "Club": self.club
        }

class Season: #holds match data, player squad, and stats summary for a specific club season
    def __init__(self, year, match_df=None, squad=None):
        self.year = str(year)  # full season string (2022-2023)
        self.match_df = match_df
        self.squad = squad or []  # list of player objects
        self.summary = {}

    def _generate_summary(self): #use match data to compute stats summary
        team_name = self.match_df['home_team'].iloc[0]
        self.summary = generate_stats_summary(self.match_df, team_name)

    def get_summary(self): #return the stats summary, generating it if not already done
        if not self.summary and self.match_df is not None and not self.match_df.empty:
            self._generate_summary()
        return self.summary

class League: #stores path to db and lazily queries match/player data
    def __init__(self, db_path):
        self.db_path = db_path  # path to sqlite db
        self.club_seasons = {}

    def _connect(self): #helper to open sqlite connection
        return sqlite3.connect(self.db_path)

    def get_valid_seasons(self, club):
        with self._connect() as conn:
            # get match seasons
            results = pd.read_sql(
                "SELECT DISTINCT season FROM goals WHERE lower(home_team) = ? OR lower(away_team) = ?",
                conn, params=(club, club)
            )['season'].dropna().astype(str)

            # get player seasons
            players = pd.read_sql(
                "SELECT DISTINCT Season FROM players WHERE lower(Club) = ?",
                conn, params=(club,)
            )['Season'].dropna().astype(str)

        # filter only season strings in YYYY-YYYY format
        results = results[results.str.len() == 9]
        players = players[players.str.len() == 9]

        all_seasons = sorted(set(results) | set(players))
        return all_seasons

    def get_season(self, club, season): #construct Season object on-demand for club + season
        season_str = str(season)
        season_start = season_str.split('-')[0]

        with self._connect() as conn:
            club_df = pd.read_sql(
                f"""
                SELECT * FROM goals
                WHERE season = ? AND (lower(home_team) = ? OR lower(away_team) = ?)
                """,
                conn, params=(season_str, club, club)
            )

            player_df = pd.read_sql(
                f"""
                SELECT * FROM players
                WHERE lower(Club) = ? AND Season = ?
                """,
                conn, params=(club, season_start)
            )

        squad = [Player(
            row.get("Name"),
            row.get("Position"),
            row.get("Age"),
            row.get("Nationality"),
            row.get("Market Value (€)"),
            season_str,
            club
        ) for _, row in player_df.iterrows()]

        return Season(season_str, match_df=club_df, squad=squad)

    def get_all_matches(self, club): #return a combined df of matches across all seasons for a given club
        with self._connect() as conn:
            df = pd.read_sql(
                f"""
                SELECT * FROM goals
                WHERE lower(home_team) = ? OR lower(away_team) = ?
                """,
                conn, params=(club, club)
            )
        return df

    def get_all_players(self, club): #return all players across all seasons for a given club
        with self._connect() as conn:
            rows = pd.read_sql(
                f"""
                SELECT * FROM players
                WHERE lower(Club) = ?
                """,
                conn, params=(club,)
            )
        return rows.to_dict(orient='records')

    def get_player_by_fuzzy_name(self, name, n=1, cutoff=0.7): #return closest player match using fuzzy matching
        import difflib
        with self._connect() as conn:
            df = pd.read_sql("SELECT DISTINCT Name FROM players WHERE Name IS NOT NULL", conn)
            all_names = df['Name'].dropna().unique().tolist()

        matches = difflib.get_close_matches(name, all_names, n=n, cutoff=cutoff)
        if not matches:
            return None

        with self._connect() as conn:
            player_df = pd.read_sql(
                "SELECT * FROM players WHERE Name = ?",
                conn, params=(matches[0],)
            )
        return player_df.iloc[0].to_dict() if not player_df.empty else None

    def get_combined_match_df(self): #return all matches across all clubs
        with self._connect() as conn:
            return pd.read_sql("SELECT * FROM goals", conn)