import json
import webbrowser
import numpy as np
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
import aws_utils as aut

def lambda_handler(event, context):
    # Retrieve client id & secret for Spotify OAuth from AWS Secrets Manager
    client_id, client_secret, redirect_uri, _ = aut.retrieve_secret_prod()
    
    # Create Spotipy instance
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='user-read-private user-read-email user-read-recently-played',
        open_browser=False
    )
    auth_url = sp_oauth.get_authorize_url()
    
    print(auth_url)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Auth URL created successfully.')
    }
