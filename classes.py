from analytics.stats import filter_club_season, generate_stats_summary
import pandas as pd

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

class League: #stores data paths and gives lazy access to club/season data
    def __init__(self, match_data_path, goal_data_path, player_data_path):
        self.match_data_path = match_data_path
        self.goal_data_path = goal_data_path
        self.player_data_path = player_data_path
        self.gs = None
        self.players = None
        self.club_seasons = {}

    def load(self): #load raw data only
        from analytics.data_load import load_data
        self.gs, self.players = load_data()

    def get_valid_seasons(self, club): #compute valid seasons lazily for a given club
        if self.gs is None:
            return []

        all_seasons = sorted(self.gs['season'].dropna().unique())
        valid = []
        for season in all_seasons:
            season_str = str(season)
            season_start = season_str.split('-')[0]
            club_df = filter_club_season(self.gs, club, season_str)
            player_df = self.players[
                (self.players['Club'] == club) & (self.players['Season'] == season_start)
            ]
            if not club_df.empty or not player_df.empty:
                valid.append(season_str)
        return valid

    def get_season(self, club, season): #construct Season object on-demand for club + season
        season_str = str(season)
        season_start = season_str.split('-')[0]

        club_df = filter_club_season(self.gs, club, season_str)
        player_df = self.players[(self.players['Club'] == club) & (self.players['Season'] == season_start)]

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
        all_seasons = self.get_valid_seasons(club)
        dfs = [filter_club_season(self.gs, club, s) for s in all_seasons]
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def get_all_players(self, club): #return all players across all seasons for a given club
        rows = self.players[self.players['Club'] == club]
        return rows.to_dict(orient='records')

    def get_player_by_fuzzy_name(self, name, n=1, cutoff=0.7): #return closest player match using fuzzy matching
        import difflib
        all_names = self.players['Name'].dropna().unique().tolist()
        matches = difflib.get_close_matches(name, all_names, n=n, cutoff=cutoff)
        if not matches:
            return None
        return self.players[self.players['Name'] == matches[0]].iloc[0].to_dict()

    def get_combined_match_df(self): #return all matches across all clubs
        return self.gs.copy() if self.gs is not None else pd.DataFrame()