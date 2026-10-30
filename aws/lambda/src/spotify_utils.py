from datetime import datetime, timedelta
import requests
import time
import json
import uuid
import numpy as np
import pandas as pd


def get_timestamp_after(offset: int = 1):
    """"""
    now = int(datetime.now().timestamp())
    now_less_offset = now - (60 * 60 * 24 * offset)  # 60 * 60 * 24 to get seconds per day
    return now_less_offset * 1_000

def fetch_audio_features_reccobeats(data: pd.DataFrame, max_retries: int = 3) -> dict:
    """Fetch audio features from ReccoBeats API as Spotify API is deprecated for this endpoint."""
    # Prepare request to ReccoBeats API
    track_id_inputs = list(data['track_id'].drop_duplicates().values)
    track_id_string = ','.join(track_id_inputs)
    url = f"https://api.reccobeats.com/v1/audio-features?ids={track_id_string}"
    payload = {}
    headers = {
        'Accept': 'application/json'
    }

    # Retry fetching audio features with exponential backoff until max_retries is reached
    for attempt in range(max_retries+1):
        try:
            # Make the request to ReccoBeats API to get audio features
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status() # Raises HTTPError for bad status codes
            return response.json(), response.status_code

        except (requests.exceptions.RequestException, requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s, 8s, ...
                print(f"Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"ReccoBeats API unavailable after {max_retries} attempts: {e}")
                return {}, response.status_code

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

            result_dict['first_artist_id'] = artist_id_list[0]
            result_dict['combined_artist_id'] = "_".join(artist_id_list)
            if len(artist_name_list) == 1:
                result_dict['first_artist_name'] = artist_name_list[0]
                result_dict['combined_artist_names'] = artist_name_list[0]
                result_dict['is_solo_artist'] = True
            elif len(artist_name_list) == 2:
                result_dict['first_artist_name'] = artist_name_list[0]
                result_dict['combined_artist_names'] = " & ".join(artist_name_list)
                result_dict['is_solo_artist'] = False
            else:
                result_dict['first_artist_name'] = artist_name_list[0]
                artist_names = ", ".join(artist_name_list[:-1])
                result_dict['combined_artist_names'] = " & ".join([artist_names, artist_name_list[-1]])
                result_dict['is_solo_artist'] = False

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


def parse_artists_json(req: json) -> pd.DataFrame:
    """"""
    artist_id_list = []
    artist_followers_list = []
    artist_popularity_list = []
    artist_genres_list = []
    artist_image_url_list = []
    artist_image_height_list = []
    artist_image_width_list = []

    for i in range(len(req['artists'])):
        artist_id_list.append(req['artists'][i]['id'])
        artist_followers_list.append(req['artists'][i]['followers']['total'])
        artist_popularity_list.append(req['artists'][i]['popularity'])
        artist_image_url_list.append(req['artists'][i]['images'][0]['url'])
        artist_image_height_list.append(req['artists'][i]['images'][0]['height'])
        artist_image_width_list.append(req['artists'][i]['images'][0]['width'])
        artist_genres = ", ".join(req['artists'][i]['genres'])

        if artist_genres == '':
            artist_genres = np.nan
        artist_genres_list.append(artist_genres)

    result_df = pd.DataFrame({
        'first_artist_id': artist_id_list
        , 'artist_followers_total': artist_followers_list
        , 'artist_popularity': artist_popularity_list
        , 'artist_genres': artist_genres_list
        , 'artist_image_url': artist_image_url_list
        , 'artist_image_height': artist_image_height_list
        , 'artist_image_width': artist_image_width_list
    })

    return result_df


def parse_albums_json(req: json) -> pd.DataFrame:
    """"""
    album_id_list = []
    album_popularity_list = []
    album_genres_list = []
    album_image_url_list = []
    album_image_height_list = []
    album_image_width_list = []

    for i in range(len(req['albums'])):
        album_id_list.append(req['albums'][i]['id'])
        album_popularity_list.append(req['albums'][i]['popularity'])
        album_image_url_list.append(req['albums'][i]['images'][0]['url'])
        album_image_height_list.append(req['albums'][i]['images'][0]['height'])
        album_image_width_list.append(req['albums'][i]['images'][0]['width'])
        album_genres = ", ".join(req['albums'][i]['genres'])
        if album_genres == '':
            album_genres = np.nan
        album_genres_list.append(album_genres)

    result_df = pd.DataFrame({
        'album_id': album_id_list
        , 'album_popularity': album_popularity_list
        , 'album_genres': album_genres_list
        , 'album_image_url': album_image_url_list
        , 'album_image_height': album_image_height_list
        , 'album_image_width': album_image_width_list
    })

    return result_df


def parse_audio_features_spotify_json(req: json) -> pd.DataFrame:
    """"""
    result_df_list = []

    for i in range(len(req)):
        result_dict = {}
        for feat in ['id', 'acousticness', 'danceability', 'energy', 'key', 'instrumentalness', 'speechiness', 'loudness',
                     'tempo', 'valence']:
            result_dict[feat] = [req[i][feat]]

        temp_df = pd.DataFrame(result_dict)
        result_df_list.append(temp_df)

    result_df = pd.concat(result_df_list, axis=0).reset_index(drop=True)
    result_df = result_df.rename(columns={'id': 'track_id'})

    return result_df


def parse_audio_features_reccobeats_json(response: dict) -> pd.DataFrame:
    """Parse the ReccoBeats API response to a pandas DataFrame."""
    # Check if response contains audio features (i.e. audio features are available for the requested track IDs)...
    if len(response['content'])>0:
        df_list = []
        # Iterate through each item in the response
        # Note: 'content'-layer contains one dict per track, given that audio features are available for that track. 
        for item in response['content']: 
            parsed_df = pd.DataFrame(item, index=[0])
            df_list.append(parsed_df)
        track_df = pd.concat(df_list, axis=0).reset_index(drop=True)
        track_df['track_id'] = track_df['href'].str.split('/').str[-1]
        track_df = pd.concat([
            track_df.loc[:, ['track_id']]
            , track_df.loc[:, 'acousticness':'valence']
        ], axis=1)
        return track_df
    
    # ...otherwise the response for this track is empty.
    else:
        print("No audio features found in ReccoBeats response for requested track_ids.")
        return pd.DataFrame()
    