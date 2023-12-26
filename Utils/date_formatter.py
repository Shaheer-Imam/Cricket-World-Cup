from datetime import datetime

class DateFormatter(object):

    @staticmethod
    def convert_date_to_DDMMYY(date_str):
        date_obj = datetime.strptime(date_str, "%a, %d %b '%y")
        formatted_date = date_obj.strftime("%d/%m/%y")
        return formatted_date