from bs4 import BeautifulSoup
import requests
import re

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

    def scrap_data_from_scorecard(self, scorecard):
        score_rows = scorecard.find_all("tr", {"class": ""})
        for row in score_rows[:10]:
            is_out = 0
            play_stats = row.find_all("td", {"class": "ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-text-right"})
            player_name = row.find("span", "ds-text-tight-s ds-font-medium ds-text-typo ds-underline ds-decoration-ui-stroke hover:ds-text-typo-primary hover:ds-decoration-ui-stroke-primary ds-block ds-cursor-pointer").text
            cleaned_player_name = re.sub(r'\xa0', '', player_name)
            player_score = row.find("td", "ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-text-right ds-text-typo").text
            balls_faced = play_stats[0]
            fours = play_stats[2]
            sixes = play_stats[3]
            strike_rate = play_stats[4]
            out = row.find("span", "ds-flex ds-cursor-pointer ds-items-center")
            if out:
                out = 1
                dismissal_type = out.text
            else:
                dismissal_type = "not out"

            data_json = {
                "player_name": cleaned_player_name,
                "player_score": player_score,
                "balls_faced": balls_faced,
                "fours": fours,
                "sixes": sixes,
                "strike_rate": strike_rate,
                "is_out": out,
                "dismissal_type": dismissal_type
            }



    def get_html(self):
        req = requests.get(self.url)
        if req.status_code == 404:
            raise "Tournament not found"
        else:
            return BeautifulSoup(req.text, 'html.parser')