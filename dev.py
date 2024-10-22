import sys
import os
from datetime import datetime, timedelta
import yaml
import webbrowser
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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
token_info = sp_oauth.refresh_access_token(refresh_token='AQCTbBqX6fczhF5lfXg5YFKXqGEZAngRx0QY9P1jIsoGApfmYNaAkiH9uTo4ONRkfO62RmPV6dWoO4lG_zON99Qx1eGqOkNdrbodTVb-pdlPXPd4kBvipMJuckWoOesmh-Q')
token_info['access_token']



"""
auth_url = sp_oauth.get_authorize_url()
print(auth_url)
webbrowser.open(auth_url)


sp_oauth.get_authorization_code()
sp_oauth._open_auth_url()
sp_oauth.get
"""