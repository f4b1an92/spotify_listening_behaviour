import sys
import os
import requests
from datetime import datetime, timedelta
import yaml
import webbrowser
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

# Folder of this script (aws/local_development); the repo root is two levels up
PATH = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(PATH))

DATA_PATH = os.path.join(REPO_ROOT, 'data')

sys.path.append(os.path.join(REPO_ROOT, 'aws', 'lambda', 'src'))
import spotify_utils as ut

# Load config & use it to define constants
with open(PATH + '/config/aws_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

CLIENT_ID = config['client_id']  # Needs to come from AWS Secrets Manager
CLIENT_SECRET = config['client_secret']  # Needs to come from AWS Secrets Manager
REFRESH_TOKEN = config['refresh_token']  # Needs to come from AWS Secrets Manager
REDIRECT_URI = config['redirect_uri_aws']  # ToDo: Check which redirect URI can be used on AWS Lambda
OFFSET = config['offset']
LIMIT = config['limit']

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope='user-read-private user-read-email user-read-recently-played',
    open_browser=False
)
token_info = sp_oauth.refresh_access_token(refresh_token=REFRESH_TOKEN)
access_token = token_info['access_token']

# Use AccessToken to get recently played user track
sp = spotipy.Spotify(auth=access_token) 

after_thr = ut.get_timestamp_after(offset=1)  # offset in days
recently_played = sp.current_user_recently_played(
    limit=50, after=after_thr, before=None
)

# Parse JSON to pandas.DataFrame
data = ut.parse_recently_played_json(req=recently_played)
print(data.shape)

# Parse Artist Response
artist_id_inputs = list(data['first_artist_id'].drop_duplicates().values)
artists_response = sp.artists(artists=artist_id_inputs)

artist_df = ut.parse_artists_json(req=artists_response)


# Parse Album response
album_id_inputs = list(data['album_id'].drop_duplicates().values)
albums_response = sp.albums(albums=album_id_inputs)

albums_df = ut.parse_albums_json(req=albums_response)

# Fetch and parse audio features
# Distinguish between cases with more than 40 unique track IDs (ReccoBeats API limitation) and less than 40 unique track IDs
if len(data['track_id'].drop_duplicates().values) > 40:
    track_df_subset_list = []
    track_id_inputs = list(data['track_id'].drop_duplicates().values)
    a = np.arange(0, len(track_id_inputs), 40)
    b = np.append(a[1:], len(track_id_inputs))
    for lower, upper in zip(a, b):
        track_id_subset = track_id_inputs[lower:upper]
        audio_features_response, status_code = ut.fetch_audio_features_reccobeats(data=data.loc[data['track_id'].isin(track_id_subset)])
        track_df_subset = ut.parse_audio_features_reccobeats_json(response=audio_features_response)
        track_df_subset_list.append(track_df_subset)
    track_df = pd.concat(track_df_subset_list, axis=0).reset_index(drop=True)
else:
    audio_features_response, status_code = ut.fetch_audio_features_reccobeats(data=data)
    track_df = ut.parse_audio_features_reccobeats_json(response=audio_features_response)

# Merge artist, album and track features with recently played tracks
data = data.merge(artist_df, how='left', on='first_artist_id')
data = data.merge(albums_df, how='left', on='album_id')
if track_df.empty:
    feature_names_list = ['track_id', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'valence']
    track_df = pd.DataFrame({
        k: np.tile([np.nan], len(data)) for k in feature_names_list
    })
    data = pd.concat([data, track_df], axis=1)
else:
    data = data.merge(track_df, how='left', on='track_id')
print(data.shape)

# Restructure column order in final dataframe
data = pd.concat([
    data.loc[:, 'id':'track_popularity']
    , data.loc[:, 'acousticness':'valence']
    , data.loc[:, 'first_artist_id':'is_solo_artist']
    , data.loc[:, 'artist_followers_total':'artist_image_width']
    , data.loc[:, 'album_id':'album_total_tracks']
    , data.loc[:, 'album_popularity':'album_image_width']
    , data.loc[:, 'played_at':'after']
], axis=1)
print(data.shape)

