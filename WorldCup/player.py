from bs4 import BeautifulSoup
import requests

class Player(object):
    def __init__(self, player_id, cricinfo_player_id, is_captain, team_id, team_name):
        self.player_id = player_id
        self.cricinfo_player_id = cricinfo_player_id
        self.team_id = team_id
        self.team_name = team_name
        self.html_url = f"https://www.espncricinfo.com/player/player-name-{cricinfo_player_id}"
        self.json_url = f"http://core.espnuk.org/v2/sports/cricket/athletes/{cricinfo_player_id}"
        self.html = self.get_html()
        self.json = self.get_json()
        self.name = self.get_name()
        self.first_name = self.get_first_name()
        self.last_name = self.get_last_name()
        self.full_name = self.get_full_name()
        self.dob = self.get_dob()
        self.age = self.get_age()
        self.role = self.get_role()
        self.captain = is_captain
        self.batting_style = self.get_batting_style()
        self.bowling_style = self.get_bowling_style()
        self.is_batsman = self.is_player_batsman()
        self.is_bowler = self.is_player_bowler()
        self.is_allrounder = self.is_player_allrounder()
        self.is_wicketkeeper = self.get_is_wicketkeeper()

    def get_html(self):
        req = requests.get(self.html_url)
        if req.status_code == 404:
            raise "Player not found"
        else:
            return BeautifulSoup(req.text, "html.parser")

    def get_json(self):
        req = requests.get(self.json_url)
        if req.status_code == 404:
            raise "Player not found"
        else:
            return req.json()

    def get_name(self):
        return self.json["name"]

    def get_first_name(self):
        return self.json["firstName"]

    def get_last_name(self):
        return self.json["lastName"]

    def get_full_name(self):
        return self.json["fullName"]

    def get_dob(self):
        return self.json["dateOfBirth"]

    def get_age(self):
        return self.json["age"]

    def get_role(self):
        return self.json["position"]

    def get_batting_style(self):
        return next((x for x in self.json['style'] if x['type'] == 'batting'), None)

    def get_bowling_style(self):
        return next((x for x in self.json['style'] if x['type'] == 'bowling'), None)

    def is_player_batsman(self):
        return "batter" in self.role['name'].lower()

    def is_player_bowler(self):
        return "bowler" in self.role['name'].lower()

    def is_player_allrounder(self):
        return "allrounder" in self.role['name'].lower()

    def get_is_wicketkeeper(self):
        return "wicketkeeper" in self.role["name"].lower()

    def toJson(self):
        if self.bowling_style is not None:
            bowling_style = self.bowling_style["description"]
        else:
            bowling_style = None

        json = {
            "player_id": self.player_id,
            "cricinfo_player_id": self.cricinfo_player_id,
            "name": self.name,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "date_of_birth": self.dob,
            "age": self.age,
            "role": self.role["name"],
            "captain": self.captain,
            "batting_style": self.batting_style["description"],
            "bowling_style": bowling_style,
            "is_batsman": 1 if self.is_batsman else 0,
            "is_bowler": 1 if self.is_bowler else 0,
            "is_allrounder": 1 if self.is_allrounder else 0,
            "is_wicketkeeper": 1 if self.is_wicketkeeper else 0
        }
        return json