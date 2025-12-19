import sys
import os
from datetime import datetime, timedelta
import yaml
import webbrowser
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

# Define main path (this should give the same path independant of the execution env (i.e. terminal, Jupyter NB or IDE))
if sys.stdin.isatty() & sys.stdout.isatty():
    PATH = os.path.dirname(os.path.abspath(__file__))  # for terminal
elif 'ipykernel' in sys.modules:
    PATH = os.path.dirname(os.path.abspath(""))  # for Jupyter notebook
else:
    PATH = os.getcwd()  # for IDE

MAIN_PATH = PATH + '\\Spotify'
DATA_PATH = MAIN_PATH + '\\data'

sys.path.extend([
    MAIN_PATH
])
import utils as ut

# Load config & use it to define constants
with open(MAIN_PATH + '\\resources\\config.yaml', 'r') as f:
    config = yaml.safe_load(f)

CLIENT_ID = config['client_id']  # Needs to come from AWS Secrets Manager
CLIENT_SECRET = config['client_secret']  # Needs to come from AWS Secrets Manager
REFRESH_TOKEN = config['refresh_token']  # Needs to come from AWS Secrets Manager
#REDIRECT_URI = config['redirect_uri']  # ToDo: Check which redirect URI can be used on AWS Lambda
#REDIRECT_URI = 'https://2hrguq0is4.execute-api.eu-central-1.amazonaws.com/dev/API_gateway_test_get' # Redirect URI if you want to check the auth response from Spotify (JSON message)
REDIRECT_URI = 'https://g35l66k9qj.execute-api.eu-central-1.amazonaws.com/get_auth_code'

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
sp = spotipy.Spotify(auth=access_token)  # sp = spotipy.Spotify(auth_manager=sp_oauth)

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

# Parse track response
track_id_inputs = list(data['track_id'].drop_duplicates().values)
try:
    track_response = sp.audio_features(tracks=track_id_inputs)
    track_df = ut.parse_audio_features_json(req=track_response)
except SpotifyException as err:
    if err.http_status == 403:
        track_df = pd.DataFrame({
            'track_id': track_id_inputs
            , 'acousticness': np.tile([np.nan], len(track_id_inputs))
            , 'danceability': np.tile([np.nan], len(track_id_inputs))
            , 'energy': np.tile([np.nan], len(track_id_inputs))
            , 'key': np.tile([np.nan], len(track_id_inputs))
            , 'instrumentalness': np.tile([np.nan], len(track_id_inputs))
            , 'speechiness': np.tile([np.nan], len(track_id_inputs))
            , 'loudness': np.tile([np.nan], len(track_id_inputs))
            , 'tempo': np.tile([np.nan], len(track_id_inputs))
            , 'valence': np.tile([np.nan], len(track_id_inputs))
        })
    else:
        raise

# Merge artist, album and track features with recently played tracks
data = data.merge(artist_df, how='left', on='first_artist_id')
data = data.merge(albums_df, how='left', on='album_id')
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

"""
auth_url = sp_oauth.get_authorize_url()
print(auth_url)
webbrowser.open(auth_url)


sp_oauth.get_authorization_code()
sp_oauth._open_auth_url()
sp_oauth.get
"""

