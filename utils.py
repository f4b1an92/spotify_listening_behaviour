from datetime import datetime, timedelta
import json
import uuid
import numpy as np
import pandas as pd


def get_timestamp_after(offset: int = 1):
    """"""
    now = int(datetime.now().timestamp())
    now_less_offset = now - (60 * 60 * 24 * offset)  # 60 * 60 * 24 to get seconds per day
    return now_less_offset * 1_000

def parse_recently_played_json(req: json) -> pd.DataFrame:
    """"""
    df_list = []
    for i in range(len(req['items'])):
        result_dict = {}
        result_dict['id'] = str(uuid.uuid4())  # generates unique ID for this entry in the dataframe

        # track-loop
        for elem in ['id', 'name', 'duration_ms', 'is_local', 'popularity']:
            result_dict[f'track_{elem}'] = req['items'][i]['track'][elem]

        # artist-loop
        if len(req['items'][i]['track']['artists']) > 0:
            artist_id_list = []
            artist_name_list = []
            for j in range(len(req['items'][i]['track']['artists'])):
                artist_id = req['items'][i]['track']['artists'][j]['id']
                artist_name = req['items'][i]['track']['artists'][j]['name']
                artist_id_list.append(artist_id)
                artist_name_list.append(artist_name)

            result_dict['combined_artist_id'] = "_".join(artist_id_list)
            if len(artist_name_list) == 1:
                result_dict['is_solo_artist'] = True
                result_dict['combined_artist_names'] = artist_name_list[0]
            elif len(artist_name_list) == 2:
                result_dict['is_solo_artist'] = False
                result_dict['combined_artist_names'] = " & ".join(artist_name_list)
            else:
                result_dict['is_solo_artist'] = False
                artist_names = ", ".join(artist_name_list[:-1])
                result_dict['combined_artist_names'] = " & ".join([artist_names, artist_name_list[-1]])

        # album-loop
        for elem in ['id', 'album_type', 'name', 'release_date', 'total_tracks']:
            if elem == 'album_type':
                result_dict[f'{elem}'] = req['items'][i]['track']['album'][elem]  # Album ID
            else:
                result_dict[f'album_{elem}'] = req['items'][i]['track']['album'][elem]  # Album ID

        # meta data
        result_dict['played_at'] = req['items'][i]['played_at']
        if not req['items'][i]['context']:
            result_dict['context_type'] = np.nan
            result_dict['context_url'] = np.nan
        else:
            result_dict['context_type'] = req['items'][i]['context']['type']  # usually equal to 'playlist'
            result_dict['context_url'] = req['items'][i]['context']['external_urls'][
                'spotify']  # link to playlist on Spotify

        df = pd.DataFrame(result_dict, index=[0])
        df_list.append(df)

    result_df = pd.concat(df_list, axis=0).reset_index(drop=True)
    result_df['before'] = req['cursors']['before']  # unix timestamp that indicates timestamp of data query
    result_df['after'] = req['cursors'][
        'after']  # unix timestamp that indicates cutoff/offset from timestamp of data query (lower thr.)

    return result_df
