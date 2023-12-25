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
        if self.json:
            self.status = self._status()
            self.match_class = self._match_class()

    def get_json(self):
        req = requests.get(self.match_url_json)
        if req.status_code == 404:
            raise "Match not found"
        else:
            return req.json()

    def get_html(self):
        req = requests.get(self.match_url_html)
        if req.status_code == 404:
            raise "Match not found"
        else:
            return BeautifulSoup(req.text, 'html.parser')

    def get_commentary_json(self):
        try:
            text = self.html.find_all('script')[15].string
            return json.loads(text)
        except Exception as err:
            return None

    def _status(self):
        return self.json['match']['match_status']

    def _match_class(self):
        class_card = None
        if self.json['match']['international_class_card'] != "":
            class_card = self.json['match']['international_class_card']
        else:
            class_card = self.json['match']['general_class_card']
        return class_card