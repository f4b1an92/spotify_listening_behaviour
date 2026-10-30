import json
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import aws_utils as aut
import spotify_utils as sut

def lambda_handler(event, context):
    try:
        # Load UserID, UserSecret and RefreshToken from AWS Secrets Manager
        client_id, client_secret, redirect_uri, refresh_token = aut.retrieve_secret_prod()
        
        # Get new AccessToken using the UserID, UserSecret & RefreshToken 
        sp_oauth = SpotifyOAuth(
                client_id=client_id
                , client_secret=client_secret
                , redirect_uri=redirect_uri
                , scope='user-read-private user-read-email user-read-recently-played'
                , show_dialog=False
                , requests_session=True
                , open_browser=False
                )
        token_info = sp_oauth.refresh_access_token(refresh_token=refresh_token)
        access_token = token_info['access_token']
        
        # Use AccessToken to get recently played user track
        sp = spotipy.Spotify(auth=access_token) #sp = spotipy.Spotify(auth_manager=sp_oauth)
        
        # Parse recently played tracks response
        after_thr = sut.get_timestamp_after(offset=1)  # offset in days
        recently_played = sp.current_user_recently_played(
            limit=50, after=after_thr, before=None
        )
        data = sut.parse_recently_played_json(req=recently_played)
        
        # Parse artist Response
        artist_id_inputs = list(data['first_artist_id'].drop_duplicates().values)
        artists_response = sp.artists(artists=artist_id_inputs)
        artist_df = sut.parse_artists_json(req=artists_response)

        # Parse album response
        album_id_inputs = list(data['album_id'].drop_duplicates().values)
        aidi_length = len(album_id_inputs)
        if aidi_length > 20:  # 20 is the maximum number of album IDs one can query at once
            albums_df_list = []
            for i, j in zip(np.arange(0, aidi_length, 20), np.arange(20, aidi_length+20, 20)):
                albums_response = sp.albums(albums=album_id_inputs[i:j])
                albums_df_list.append(sut.parse_albums_json(req=albums_response))
            albums_df = pd.concat(albums_df_list,axis=0).reset_index(drop=True)
        else:
            albums_response = sp.albums(albums=album_id_inputs)
            albums_df = sut.parse_albums_json(req=albums_response)

        # Fetch and parse audio features
        # Distinguish between cases with more than 40 unique track IDs (ReccoBeats API limitation) and less than 40 unique track IDs
        if len(data['track_id'].drop_duplicates().values) > 40:
            track_df_subset_list = []
            track_id_inputs = list(data['track_id'].drop_duplicates().values)
            a = np.arange(0, len(track_id_inputs), 40)
            b = np.append(a[1:], len(track_id_inputs))
            for lower, upper in zip(a, b):
                track_id_subset = track_id_inputs[lower:upper]
                audio_features_response, status_code = sut.fetch_audio_features_reccobeats(data=data.loc[data['track_id'].isin(track_id_subset)])
                track_df_subset = sut.parse_audio_features_reccobeats_json(response=audio_features_response)
                track_df_subset_list.append(track_df_subset)
            track_df = pd.concat(track_df_subset_list, axis=0).reset_index(drop=True)
        else:
            audio_features_response, status_code = sut.fetch_audio_features_reccobeats(data=data)
            track_df = sut.parse_audio_features_reccobeats_json(response=audio_features_response)

        # Merge artist, album and track features with recently played tracks
        data = data.merge(artist_df, how='left', on='first_artist_id')
        data = data.merge(albums_df, how='left', on='album_id')
        if track_df.empty: # if dataframe that should contain track features is empty, add empty columns via pd.concat...
            feature_names_list = ['track_id', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'valence']
            track_df = pd.DataFrame({
                k: np.tile([np.nan], len(data)) for k in feature_names_list
            })
            data = pd.concat([data, track_df], axis=1)
        else: # ... otherwise add them via left join
            data = data.merge(track_df, how='left', on='track_id')
        
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

        # Store dataframe as csv-file in S3-bucket
        aut.write_recently_played_user_tracks_to_s3(data=data)
    
        # Return message that lambda function ran successfully
        return { 
          'statusCode': 200, 
          'body': 'Recently played tracks uploaded successfully to S3.' 
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error'
            })
        }
