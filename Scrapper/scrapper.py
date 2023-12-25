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

    def get_html(self):
        req = requests.get(self.url)
        if req.status_code == 404:
            raise "Tournament not found"
        else:
            return BeautifulSoup(req.text, 'html.parser')