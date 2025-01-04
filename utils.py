import pandas as pd

class Utils:
    @staticmethod
    def get_level_ids(csv_file):
        return [{'label': row['id'], 'value': row['id']} for _, row in pd.read_csv(csv_file).iterrows()]