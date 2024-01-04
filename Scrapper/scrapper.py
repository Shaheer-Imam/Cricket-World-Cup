from bs4 import BeautifulSoup
import requests
import re
from Utils.utils import Utils

class Scrapper(object):
    def __init__(self, url):
        self.url = url
        self.html = self.get_html()

    def get_match_ids(self):
        match_ids = []
        matches_tag = self.get_all_matches_links()
        for match_tag in matches_tag:
            match_id = match_tag.get('href').split("/")[-2].split("-")[-1]
            match_ids.append(match_id)
        return match_ids

    def get_all_matches_links(self):
        div_tag = self.html.find_all('div', {'class': 'ds-mb-4'})[0]
        hrefs = div_tag.find_all('a', {'class': 'ds-no-tap-higlight'})
        return hrefs

    def get_points_table(self):
        points_tbody = self.html.find('tbody', 'ds-text-center')
        points_rows = points_tbody.find_all("tr",{"class":"ds-text-tight-s ds-text-typo-mid2"})
        return points_rows

    def get_teams(self):
        teams_div = self.html.find("div", "ds-flex ds-space-x-5")
        teams_span = teams_div.find_all("span", {"class": "ds-text-title-s ds-font-bold"})
        return teams_span

    def get_squad_url(self):
        squad_url = self.html.find_all("a", {"class" : "ds-inline-flex ds-items-start ds-leading-none"})
        urls = [url.get('href') for url in squad_url][:10]
        return urls

    def get_squad_player_ids(self):
        players = []
        main_divs = self.html.find("div","ds-mb-4")
        player_divs = main_divs.find_all("div", {"class": "ds-border-line odd:ds-border-r ds-border-b"})
        for player in player_divs:
            captain_span = player.find("span", {"class":"ds-text-tight-m ds-font-medium"})
            player_data = {
                "is_captain": captain_span == None,
                "cricinfo_player_id": player.find("a", "ds-cursor-pointer").get("href").split("-")[-1]
            }
            players.append(player_data)
        return players

    def scrap_tournament_fixtures(self):
        main_div = self.html.find("div","ds-p-0")
        fixtures_div = main_div.find_all("div",{"class":"ds-p-4"})
        return fixtures_div

    def scrap_scorecard(self):
        scorecard_tables = self.html.find_all("table", {"class": "ds-w-full ds-table ds-table-md ds-table-auto ci-scorecard-table"})
        return scorecard_tables

    def scrap_bowling_scorecard(self):
        bowling_scorecard = self.html.find_all("table", {"class":"ds-w-full ds-table ds-table-md ds-table-auto"})
        return bowling_scorecard

    def scrap_data_from_scorecard(self, scorecard, match_id, team_id, team_name, playing_xi, players_df):
        scores = []
        score_rows = scorecard.find_all("td", class_=["ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-flex ds-items-center", "ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-flex ds-items-center ds-border-line-primary ci-scorecard-player-notout"])
        for td in score_rows:
            row = td.find_parent()
            dnb = 0
            is_out = 0
            play_stats = row.find_all("td", {"class": "ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-text-right"})
            player_name = row.find("span", "ds-text-tight-s ds-font-medium ds-text-typo ds-underline ds-decoration-ui-stroke hover:ds-text-typo-primary hover:ds-decoration-ui-stroke-primary ds-block ds-cursor-pointer").text
            player_name = Utils.clean_text_data_from_name(player_name)
            player_id = players_df.loc[players_df["name"] == player_name, "player_id"].values[0]
            runs = row.find("td", "ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-text-right ds-text-typo").text
            balls_faced = play_stats[0].text
            fours = play_stats[2].text
            sixes = play_stats[3].text
            strike_rate = play_stats[4].text
            dismissal = row.find("span", "ds-flex ds-cursor-pointer ds-items-center")
            if dismissal:
                is_out = 1
                dismissal_type = dismissal.text
            elif dismissal is None and runs == "-":
                runs = 0
                fours = 0
                sixes = 0
                strike_rate = 0.0
                dnb = 1
                balls_faced = 0
                dismissal_type = "Retired hurt"
            else:
                dismissal_type = None

            if runs == "0" and balls_faced == "0" and strike_rate == "-":
                strike_rate = 0.0

            data_json = {
                "player_name": player_name,
                "player_id": player_id,
                "team_id": team_id,
                "match_id": match_id,
                "runs": int(runs),
                "balls_faced": int(balls_faced),
                "fours": fours,
                "sixes": sixes,
                "strike_rate": float(strike_rate),
                "dnb": dnb,
                "is_out": is_out,
                "dismissal_type": dismissal_type
            }

            scores.append(data_json)

        # Some batsman did not bat
        if len(scores) != 11:
            team_playing_xi = playing_xi[team_name]
            batsmen = [value for value in team_playing_xi if not any(value in my_dict.values() for my_dict in scores)]
            for batsman in batsmen:
                batsman = Utils.clean_text_data_from_name(batsman)
                player_id = players_df.loc[players_df["name"] == batsman, "player_id"].values[0]
                data_json = {
                    "player_name": Utils.clean_text_data_from_name(batsman),
                    "player_id": player_id,
                    "team_id": team_id,
                    "match_id": match_id,
                    "runs": 0,
                    "balls_faced": 0,
                    "fours": 0,
                    "sixes": 0,
                    "strike_rate": 0.0,
                    "dnb": 1,
                    "is_out": 0,
                    "dismissal_type": None
                }
                scores.append(data_json)

        return scores

    def scrap_playing_XI(self):
        main_table = self.html.find("table", "ds-w-full ds-table ds-table-sm ds-table-bordered ds-border-collapse ds-border ds-border-line ds-table-auto ds-bg-fill-content-prime")
        headings = main_table.find_all("th")
        team_one = headings[1].text
        team_two = headings[2].text
        playing_xi = {
            team_one: [],
            team_two: []
        }
        tbody = main_table.find("tbody")
        team_rows = tbody.find_all("tr")
        for row in team_rows[:11]:
            player_link = row.find_all("a")
            playing_xi[team_one].append(player_link[0].text.strip())
            playing_xi[team_two].append(player_link[1].text.strip())
        return playing_xi

    def get_team_name_from_scorecard(self, scorecard):
        team = scorecard.find_parent().find_previous_sibling().find("span", "ds-text-title-xs ds-font-bold ds-capitalize").text
        return team

    def get_html(self):
        req = requests.get(self.url)
        if req.status_code == 404:
            raise "Tournament not found"
        else:
            return BeautifulSoup(req.text, 'html.parser')