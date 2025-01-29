
import pandas as pd

def merge_track(table_1, table_2):
    return pd.merge(table_1, table_2, left_on='track_id', right_on='track_id', how='left')

def merge_artist(table_1, table_2):
    return pd.merge(table_1, table_2, left_on='artist_id', right_on='artist_id', how='left')
