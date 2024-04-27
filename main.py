import sys
import os
from datetime import datetime, timedelta
import yaml
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

MAIN_PATH = os.getcwd()
DATA_PATH = MAIN_PATH + '\\data'

sys.path.extend([
    MAIN_PATH
])
import utils as ut

# Load config & use it to define constants
with open(MAIN_PATH + '\\resources\\config.yaml', 'r') as f:
    config = yaml.safe_load(f)

CLIENT_ID = config['client_id']
CLIENT_SECRET = config['client_secret']
REDIRECT_URI = config['redirect_uri']

OFFSET = config['offset']
LIMIT = config['limit']




if __name__ == '__main__':
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID
            , client_secret=CLIENT_SECRET
            , redirect_uri=REDIRECT_URI
            , scope='user-read-private user-read-email user-read-recently-played'
            , show_dialog=False
            , requests_session=True
            , open_browser=False
        )
    )

    after_thr = ut.get_timestamp_after(offset=OFFSET)
    recently_played = sp.current_user_recently_played(limit=LIMIT, after=after_thr, before=None)
    result_df = ut.parse_recently_played_json(req=recently_played)

    # Store results
    today = pd.to_datetime(datetime.today()).date().strftime(format='%Y-%m-%d')
    result_df.to_csv(DATA_PATH + f'\\result_df_{today}.csv', index=False)
