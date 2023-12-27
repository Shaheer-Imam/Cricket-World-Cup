import pandas as pd
import os

class PointsTable(object):

    @staticmethod
    def get_team_points_table():
        path = os.path.join(os.getcwd(), "Datasets/points.csv")
        df = pd.read_csv(path)
        points_sorted_df = df.sort_values(by=["points","NRR"], ascending=[False, False]).drop('team_id', axis=1).reset_index(drop=True)
        return points_sorted_df