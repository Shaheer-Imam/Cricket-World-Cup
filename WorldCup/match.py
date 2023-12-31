from bs4 import BeautifulSoup
import requests
import json

class Match(object):
    def __init__(self, match_id):
        self.match_id = match_id
        self.match_url_html = f"https://www.espncricinfo.com/matches/engine/match/{match_id}.html"
        self.match_url_json = f"https://www.espncricinfo.com/matches/engine/match/{match_id}.json"
        self.json = self.get_json()
        self.html = self.get_html()
        #self.comms_json = self.get_comms_json()
        if self.json:
            self.ground_name = self.get_ground_name()
            self.playing_xi = self.get_playing_XI()

    def __str__(self):
        return self.description

    def __repr__(self):
        return (f'{self.__class__.__name__}('f'{self.match_id!r})')

    def get_json(self):
        r = requests.get(self.match_url_json)
        if r.status_code == 404:
            raise "Match Not Found"
        elif 'Scorecard not yet available' in r.text:
            raise "No Scorecard"
        else:
            return r.json()

    def get_html(self):
        r = requests.get(self.match_url_html)
        if r.status_code == 404:
            raise "Match Not Found"
        else:
            return BeautifulSoup(r.text, 'html.parser')

    def get_ground_name(self):
        return self.json["match"]["ground_name"]

    def get_team1_name(self):
        return self.json["match"]["team1_name"]

    def get_team1_abbreviation(self):
        return self.json["match"]["team1_abbreviation"]

    def get_team2_name(self):
        return self.json["match"]["team2_name"]

    def get_team2_abbreviation(self):
        return self.json["match"]["team2_abbreviation"]

    def get_playing_XI(self):
        playing_xi = {}
        teams = self.json["team"]
        for team in teams:
            #playing_xi[team["team_name"]] = self.get_team_playing_xi(team["player"])
            playing_xi[team["team_name"]] = team["player"]

    def get_team_playing_xi(self, players):
        playing_xi = {}
        for player in players:
            print(player)

