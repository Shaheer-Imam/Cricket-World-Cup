from WorldCup.match import Match
from WorldCup.player import Player
#from WorldCup.fixture import Fixture
import csv
from .scrapper import Scrapper
import os
import json
from Utils.Constants import Constants
from Utils.date_formatter import DateFormatter
import pandas as pd
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
            team_name = team.text
            self.teams[team_name] = team_id
            team_data["team_id"] = team_id
            team_data["team_name"] = team_name
            team_data["team_abbreviation"] = Constants.TEAMS[team.text]
            team_data["flag_img"] = f"static/imgs/flags/{team_name}.jpg"
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
        teams_df = pd.read_csv(os.path.join(os.getcwd(), "Datasets/teams.csv"))

        if not os.path.exists(os.path.join(os.getcwd(),"Datasets")):
            os.mkdir("Datasets")

        dataset = []
        squads_url = self.scrap_team_squad_url()
        player_id = 1
        for team_id, squad_url in enumerate(squads_url, 1):
            url = f"https://www.espncricinfo.com{squad_url}"
            squad_page = Scrapper(url)
            players = squad_page.get_squad_player_ids()
            team_name = teams_df[teams_df["team_id"] == team_id]["team_name"].to_string(index=False)
            for p in players:
                player = Player(player_id, p["cricinfo_player_id"], p["is_captain"], team_id, team_name)
                player_json = player.toJson()
                dataset.append(player_json)
                player_id += 1
        headers = player_json.keys()
        with open("Datasets/players.csv", 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
            csv_writer.writeheader()
            csv_writer.writerows(dataset)


    def scrap_team_squad_url(self):
        team_squad_scrapper = Scrapper(self.squads_url)
        return team_squad_scrapper.get_squad_url()

    def build_fixtures_dataset(self):
        teams_df = pd.read_csv(os.path.join(os.getcwd(), "Datasets/teams.csv"))
        tournament_teams = list(teams_df["team_name"])
        matches = []
        match_links = []
        fixtures = self.scrap_fixtures()
        match_date = None
        for match_id, fixture in enumerate(fixtures, 1):
            #fixture_ = Fixture(fixture, match_id)
            is_semi_final_one = 0
            is_semi_final_two = 0
            is_final = 0
            date_str = fixture.find("div", "ds-text-compact-xs ds-font-bold ds-w-24").text
            if date_str == '':
                date_str = match_date
            scores = fixture.find_all("div", {"class": "ds-text-compact-s ds-text-typo ds-text-right ds-whitespace-nowrap"})
            teams = fixture.find_all("p", {"class": "ds-text-tight-m ds-font-bold ds-capitalize ds-truncate"})
            match_link = fixture.find("a", "ds-no-tap-higlight")
            cricinfo_match_id = match_link.get("href").split("/")[-2].split("-")[-1]
            result = fixture.find("p", {"class": "ds-text-tight-s ds-font-regular ds-line-clamp-2 ds-text-typo"}).text
            team_won = next((team for team in tournament_teams if team.lower() in result.lower()), None)
            team_won_id = self.teams[team_won]
            match_title = fixture.find("span", "ds-text-tight-s ds-font-medium ds-text-typo").text
            if "Final (D/N)" in match_title:
                is_final = 1
            if "1st Semi Final" in match_title:
                is_semi_final_one = 1
            if "2nd Semi Final" in match_title:
                is_semi_final_two = 1
            json_data = {
                "match_id": match_id,
                "cricinfo_matchid": cricinfo_match_id,
                "semi_final_1": is_semi_final_one,
                "semi_final_2": is_semi_final_two,
                "is_final": is_final,
                "date": DateFormatter.convert_date_to_DDMMYY(date_str),
                "team_one_name": teams[0].text,
                "team_one_id": self.teams[teams[0].text],
                "team_two_name": teams[1].text,
                "team_two_id": self.teams[teams[1].text],
                "team_one_score": scores[0].text,
                "team_two_score": scores[1].text.split(" ")[-1],
                "result": fixture.find("p", {"class": "ds-text-tight-s ds-font-regular ds-line-clamp-2 ds-text-typo"}).text,
                "team_won_id": team_won_id
            }
            match_links.append(match_link.get("href"))
            match_date = date_str
            matches.append(json_data)
        headers = matches[0].keys()
        with open("Datasets/fixtures.csv", 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
            csv_writer.writeheader()
            csv_writer.writerows(matches)
        return match_links

    def scrap_fixtures(self):
        scrapper = Scrapper(self.fixtures_url)
        return scrapper.scrap_tournament_fixtures()

    def build_matches_dataset(self, match_links):
        scorecard_data = []
        players_df = pd.read_csv(os.path.join(os.getcwd(),"Datasets/players.csv"))
        teams_df = pd.read_csv(os.path.join(os.getcwd(), "Datasets/teams.csv"))
        for match_id, match_link in enumerate(match_links, 1):
            main_url = f"https://www.espncricinfo.com{match_link}"
            playing_xi_url = f"https://www.espncricinfo.com{match_link.replace('full-scorecard', 'match-playing-xi')}"
            playing_eleven_scrapper = Scrapper(playing_xi_url)
            playing_xi = playing_eleven_scrapper.scrap_playing_XI()
            scrapper = Scrapper(main_url)
            scorecards = scrapper.scrap_scorecard()
            bowling_scorecards = scrapper.scrap_bowling_scorecard()
            for innings, scorecard in enumerate(scorecards, 1):
                team_name = scrapper.get_team_name_from_scorecard(scorecard)
                team_id = teams_df.loc[teams_df["team_name"] == team_name, "team_id"].values[0]
                data = scrapper.scrap_data_from_scorecard(scorecard, match_id, team_id, team_name, playing_xi, players_df, innings)
                scorecard_data.extend(data)

            for bowling_scorecard in bowling_scorecards:
                pass

        headers = scorecard_data[0].keys()
        with open("Datasets/match_scores.csv", 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
            csv_writer.writeheader()
            csv_writer.writerows(scorecard_data)

    def begin(self):
        self.build_team_dataset()
        self.build_points_table_dataset()
        self.build_squad_dataset()
        match_links = self.build_fixtures_dataset()
        self.build_matches_dataset(match_links)

    def read_config(self):
        path = os.path.join(os.getcwd(),"config.json")
        with open(path, 'r') as jsonfile:
            data = json.load(jsonfile)
        return data

if __name__ == "__main__":
    dataset = Dataset()
    dataset.begin()