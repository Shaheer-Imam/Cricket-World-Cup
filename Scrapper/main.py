from WorldCup.match import Match
from WorldCup.player import Player
import csv
from .scrapper import Scrapper
import os
import json
from Utils.Constants import Constants
from Utils.date_formatter import DateFormatter
class Dataset(object):
    def __init__(self):
        json_data = self.read_config()
        self.fixtures_url = json_data['url']['fixtures']
        self.points_url = json_data['url']['table']
        self.teams_url = json_data['url']['team']
        self.squads_url = json_data['url']['squad']
        self.build_matches = bool(json_data['dataset']['matches'])
        self.build_officials = bool(json_data['dataset']['officials'])
        self.build_team = bool(json_data['dataset']['teams'])
        self.teams = {}

    def get_world_cup_match_ids(self):
        scrapper = Scrapper(self.fixtures_url)
        return scrapper.get_match_ids()

    def start_processing(self, match_ids):
        for match_id in match_ids:
            match = Match(match_id)

    def build_team_dataset(self):
        if not os.path.exists(os.path.join(os.getcwd(),"Datasets")):
            os.mkdir("Datasets")
        teams_dataset = []
        teams = self.scrap_teams_in_tournament()
        for team_id, team in enumerate(teams,1):
            team_data = {}
            self.teams[team.text] = team_id
            team_data["team_id"] = team_id
            team_data["team_name"] = team.text
            team_data["team_abbreviation"] = Constants.TEAMS[team.text]
            teams_dataset.append(team_data)

        if self.build_team:
            headers = teams_dataset[0].keys()
            with open("Datasets/teams.csv", 'w', newline='') as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
                csv_writer.writeheader()
                csv_writer.writerows(teams_dataset)

    def build_points_table_dataset(self):
        if not os.path.exists(os.path.join(os.getcwd(),"Datasets")):
            os.mkdir("Datasets")

        points = []
        scrapper = Scrapper(self.points_url)
        points_table = scrapper.get_points_table()
        for row in points_table:
            point_data = {}
            team = row.find("span", {"class" : "ds-text-tight-s ds-font-bold ds-uppercase ds-text-left ds-text-typo"}).text
            stats = row.find_all("td", {"class" : "ds-min-w-max"})
            point_data["team_id"] = self.teams[team]
            point_data["team"] = team
            point_data["matches_played"] = stats[1].text
            point_data["won"] = stats[2].text
            point_data["lost"] = stats[3].text
            point_data["tie"] = stats[4].text
            point_data["no_result"] = stats[5].text
            point_data["points"] = stats[6].text
            point_data["NRR"] = stats[7].text
            points.append(point_data)
        sorted_team_points = sorted(points, key=lambda x:x["team_id"])
        headers = sorted_team_points[0].keys()
        with open("Datasets/points.csv", 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
            csv_writer.writeheader()
            csv_writer.writerows(sorted_team_points)

    def scrap_teams_in_tournament(self):
        team_scrapper = Scrapper(self.teams_url)
        teams = team_scrapper.get_teams()
        return teams

    def build_squad_dataset(self):
        dataset = []
        squads_url = self.scrap_team_squad_url()
        for team_id, squad_url in enumerate(squads_url, 1):
            url = f"https://www.espncricinfo.com{squad_url}"
            squad_page = Scrapper(url)
            players = squad_page.get_squad_player_ids()
            for p in players:
                player = Player(p["player_id"], p["is_captain"], team_id)
                player_json = player.toJson()
                dataset.append(player_json)
        headers = player_json.keys()
        with open("Datasets/players.csv", 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
            csv_writer.writeheader()
            csv_writer.writerows(dataset)


    def scrap_team_squad_url(self):
        team_squad_scrapper = Scrapper(self.squads_url)
        return team_squad_scrapper.get_squad_url()

    def build_fixtures_dataset(self):
        fixtures = self.scrap_fixtures()
        for match_id, fixture in enumerate(fixtures, 1):
            date_str = fixture.find("div", "ds-text-compact-xs ds-font-bold ds-w-24").text
            date = DateFormatter.convert_date_to_DDMMYY(date_str)
            match_link = fixture.find("a", "ds-no-tap-higlight")
            cricinfo_matchid = match_link.get("href").split("/")[-2].split("-")[-1]
            teams = fixture.find_all("p", {"class": "ds-text-tight-m ds-font-bold ds-capitalize ds-truncate"})
            team_one_name = teams[0].text
            team_one_id = self.teams[team_one_name]
            team_two_name = teams[1].text
            team_two_id = self.teams[team_two_name]
            scores = fixture.find_all("div", {"class": "ds-text-compact-s ds-text-typo ds-text-right ds-whitespace-nowrap"})
            team_one_score = scores[0].text
            team_two_score = scores[1].text.split(" ")[-1]
            result = fixture.find("p", {"class": "ds-text-tight-s ds-font-regular ds-line-clamp-2 ds-text-typo"}).text



    def scrap_fixtures(self):
        scrapper = Scrapper(self.fixtures_url)
        return scrapper.scrap_tournament_fixtures()

    def begin(self):
        self.build_team_dataset()
        self.build_points_table_dataset()
        #self.build_squad_dataset()
        #self.build_fixtures_dataset()
        # match_ids = self.get_world_cup_match_ids()
        # if match_ids is not None:
        #     self.start_processing(match_ids)

    def read_config(self):
        path = os.path.join(os.getcwd(),"config.json")
        with open(path, 'r') as jsonfile:
            data = json.load(jsonfile)
        return data

if __name__ == "__main__":
    dataset = Dataset()
    dataset.begin()