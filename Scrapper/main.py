from WorldCup.match import Match
import csv
from .scrapper import Scrapper
import os
import json

class Dataset(object):
    def __init__(self):
        json_data = self.read_config()
        self.url = json_data['url']
        self.scrap_matches = bool(json_data['scrap']['matches'])
        self.scrap_officials = bool(json_data['scrap']['officials'])
        self.scrap_teams = bool(json_data['scrap']['teams'])

    def get_world_cup_match_ids(self):
        scrapper = Scrapper(self.url)
        return scrapper.get_match_ids()

    def start_processing(self, match_ids):
        for match_id in match_ids:
            match = Match(match_id)

    def build_team_dataset(self, match_id):
        if not os.path.exists(os.path.join(os.getcwd(),"Datasets")):
            os.mkdir("Datasets")

        teams_dataset = []
        match = Match(match_id)
        teams = match.json["series"][0]["teams"]
        for team_id, team in enumerate(teams,1):
            team_data = {}
            team_data["team_id"] = team_id
            team_data["team_name"] = team["team_name"]
            team_data["team_abbreviation"] = team["team_abbreviation"]
            teams_dataset.append(team_data)
        headers = teams_dataset[0].keys()
        with open("Datasets/teams.csv", 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
            csv_writer.writeheader()
            csv_writer.writerows(teams_dataset)

    def begin(self):
        match_ids = self.get_world_cup_match_ids()
        if match_ids is not None:
            #self.build_team_dataset(match_ids[0])
            self.start_processing(match_ids)

    def read_config(self):
        path = os.path.join(os.getcwd(),"config.json")
        with open(path, 'r') as jsonfile:
            data = json.load(jsonfile)
        return data

if __name__ == "__main__":
    dataset = Dataset()
    dataset.begin()