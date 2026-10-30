import json
from spotipy.oauth2 import SpotifyOAuth
import aws_utils as aut

def lambda_handler(event, context):
    try:
        # Extract the authorization code from the query parameters
        authorization_code = event['queryStringParameters']['code']
        
        # Retrieve client id & secret for Spotify OAuth from AWS Secrets Manager
        client_id, client_secret, redirect_uri, _ = aut.retrieve_secret_prod()
        
        #return {'status_code': 200, 'auth_code': authorization_code}
        # Create Spotipy OAuth instance
        sp_oauth = SpotifyOAuth(
            client_id=client_id, 
            client_secret=client_secret,
            redirect_uri=redirect_uri, 
            scope='user-read-private user-read-email'
        )
        
        # Exchange authorization code for access token
        token_info = sp_oauth.get_access_token(authorization_code)
        
        
        if token_info:
            # Update the refresh_token in Secrets Manager if present
            #instance_test = isinstance(token_info['refresh_token'], str)
            if 'refresh_token' in token_info:
                aut.update_refresh_token_in_secrets_manager_prod(
                    new_refresh_token = token_info['refresh_token']
                )
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'  # Setting the content type header
                },
                'body': json.dumps({
                    'input_event': str(event),
                    #'refresh_token_type_str': str(instance_test),
                    'token_info': token_info
                })
            }
        
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'  # Setting the content type header
            },
            'body': json.dumps({'message': 'Failed to retrieve tokens'})
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