import requests
import urllib.parse
import numpy as np
import pandas as pd
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify, session

app = Flask(__name__)
app.secret_key = ''  # key to access the Flask session in which all data is stored

CLIENT_ID = ''  # ToDo: to be stored in yaml file and hidden via e.g. Vault once we migrate the script to AWS
CLIENT_SECRET = ''  # ToDo: to be stored in yaml file and hidden via e.g. Vault once we migrate the script to AWS
REDIRECT_URI = 'http://localhost:5000/callback'  #ToDo: to be changed to some AWS-specifi URL

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

OFFSET = 1  # ToDo: Should come from external yaml config-file
LIMIT = 2  # ToDo: Should come from external yaml config-file
DATA_PATH = 'C:\\Users\\fabia\\Documents\\Data Science Projects\\Media Consumption\\Spotify'  # ToDo: Should come from external yaml config-file
"""
scope = 'user-read-private user-read-email user-read-recently-played'  # ToDo: to be changed to actual scopes needed for our usecase

param_dict = {
    'client_id': CLIENT_ID
    , 'response_type': 'code'
    , 'scope': scope
    , 'redirect_uri': REDIRECT_URI # tells Spotify where to redirect request response to after login is successful (here: http://localhost:5000/callback)
    , 'show_dialog': False  # ToDo: to be set to False once we actually start automating the entire process
}
auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(param_dict)}"
test = requests.get(url=auth_url)
print(test.text)
"""

def _get_timestamp_after(offset: int = 1):
    """"""
    now = int(datetime.now().timestamp())
    now_less_offset = now - (60 * 60 * 24 * offset)  # 60 * 60 * 24 to get seconds per day
    return now_less_offset


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


@app.route('/')
def index():
    return redirect('/login') #"Welcome to my Spotify App <a href='/login'>Login with Spotify</a>"


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-read-recently-played'  # ToDo: to be changed to actual scopes needed for our usecase

    param_dict = {
        'client_id': CLIENT_ID
        , 'response_type': 'code'
        , 'scope': scope
        , 'redirect_uri': REDIRECT_URI # tells Spotify where to redirect request response to after login is successful (here: http://localhost:5000/callback)
        , 'show_dialog': False  # ToDo: to be set to False once we actually start automating the entire process
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(param_dict)}"

    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args: # request = global variable that only exists within running Flask app. Stores incoming request data after e.g. calling redirect()
        return jsonify({'error': request.args['error']})
    print(request.args['code'])
    if 'code' in request.args:
        request_body = {
            'code': request.args['code']
            , 'grant_type': 'authorization_code'
            , 'redirect_uri': REDIRECT_URI
            , 'client_id': CLIENT_ID
            , 'client_secret': CLIENT_SECRET
        }

    response = requests.post(TOKEN_URL, data=request_body)
    token_info = response.json()

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

    return redirect('/recently-played')


@app.route('/recently-played')
def get_recently_played():
    if 'access_token' not in session:
        return redirect('/login')

    if session['expires_at'] <= datetime.now().timestamp():
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    after_thr = _get_timestamp_after(offset=OFFSET)
    url_dict = {
        'limit': LIMIT
        , 'after': after_thr
    }

    response = requests.get(
        API_BASE_URL + f"me/player/recently-played?limit={url_dict['limit']}&after={url_dict['after']}"
        , headers=headers
    )
    recently_played = response.json()
    #session['raw_json'] = recently_played
    #session['parsed_json'] = parse_recently_played_json(req=recently_played)
    result_df = parse_recently_played_json(req=recently_played)
    result_df.to_csv(DATA_PATH + '\\result_df.csv', index=False)

    return jsonify(recently_played)


@app.route('/refresh_token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    request_body = {
        'grant_type': 'refresh_token'
        , 'refresh_token': session['refresh_token']
        , 'client_id': CLIENT_ID
        , 'client_secret': CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=request_body)
    new_token_info = response.json()

    session['access_token'] = new_token_info['access_token']
    session['refresh_token'] = new_token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect('/recently-played')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)

