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

CLIENT_ID = config['client_id']  # Needs to come from AWS Secrets Manager
CLIENT_SECRET = config['client_secret']  # Needs to come from AWS Secrets Manager
REDIRECT_URI = config['redirect_uri']  # ToDo: Check which redirect URI can be used on AWS Lambda

OFFSET = config['offset']
LIMIT = config['limit']




if __name__ == '__main__':
    # The following code has to go into lambda_handler()
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


# Prod Secret
# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "SpotifyOAuthCredentials"
    region_name = "eu-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']

    # Your code goes here.



# Test Secret
# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "SpotifyOAuthCredentials_TEST"
    region_name = "eu-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']

    print(secret)
