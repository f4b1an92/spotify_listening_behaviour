import sys
import os
from datetime import datetime, timedelta
import yaml
import webbrowser
import numpy as np
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

# -------------------------------------------------------------------------------------------------------------------------------------------
# NOTE: This script is used to initiate the Spotify user authentication process locally. You can also do this directly in AWS Lambda though.
# -> Lambda Function in AWS: InitiateSpotifyUserAuthentification
# -------------------------------------------------------------------------------------------------------------------------------------------

# Folder of this script (aws/local_development)
PATH = os.path.dirname(os.path.abspath(__file__))

# Load config & use it to define constants
with open(PATH + '/config/aws_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create Spotipy instance
sp_oauth = SpotifyOAuth(
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    redirect_uri=config['redirect_uri_aws'],
    scope='user-read-private user-read-email user-read-recently-played',
    open_browser=False
)
auth_url = sp_oauth.get_authorize_url()
webbrowser.open(auth_url) # opens auth_url and you will get the resulting JSON displayed in a browser window

# NOTE: Since the redirect URI is set to an endpoint in AWS Gateway, this endpoint will trigger a Lambda Function (GetSpotifyInitialAccessAndRefreshToken) that updates the refresh token in the AWS Secrets Manager.
# -> THIS MEANS: NO manual update of the refresh token is needed in AWS Secrets Manager.

# LAST STEP: After opening the auth URL in the browser, you will have to manually copy the refresh token from the resulting JSON to the local config file though as this doesn't happen automatically.
