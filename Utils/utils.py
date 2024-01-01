import re

class Utils(object):
    def clean_text_data_from_name(name_str):
        cleaned_player_name = re.sub(r'[\xa0\(].*?[\)]†', '', name_str)
        cleaned_player_name = re.sub(r'[\xa0\ (]†.*?[\)]', '', cleaned_player_name)
        cleaned_player_name = re.sub(r'[\xa0\(].*?[\)]', '', cleaned_player_name)
        cleaned_player_name = re.sub(r'[\xa0\†]', '', cleaned_player_name)
        return cleaned_player_name.strip()