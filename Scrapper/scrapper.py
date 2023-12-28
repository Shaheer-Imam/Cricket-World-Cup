from bs4 import BeautifulSoup
import requests

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

    def get_html(self):
        req = requests.get(self.url)
        if req.status_code == 404:
            raise "Tournament not found"
        else:
            return BeautifulSoup(req.text, 'html.parser')