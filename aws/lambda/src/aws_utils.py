import json
#import numpy as np
import pandas as pd
#import uuid
from datetime import datetime
import boto3
from io import StringIO
from botocore.exceptions import ClientError
import os

REGION_NAME = os.environ.get('SPOTIFY_AWS_REGION', 'eu-central-1')
SECRET_NAME_PROD = os.environ.get('SPOTIFY_SECRET_NAME', 'SpotifyOAuthCredentials')
SECRET_NAME_TEST = os.environ.get('SPOTIFY_SECRET_NAME_TEST', 'SpotifyOAuthCredentials_TEST')
DATA_BUCKET = os.environ.get('SPOTIFY_DATA_BUCKET', 'bucket-for-github-projects-fstork')
DATA_PREFIX = os.environ.get('SPOTIFY_DATA_PREFIX', 'spotify-listening-behaviour/data/created_by_lambda/')

def retrieve_secret_test():
  """Retrieves test secret from AWS Secrets Manager."""
  secret_name = SECRET_NAME_TEST
  region_name = REGION_NAME

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
      raise e

  secret = json.loads(get_secret_value_response['SecretString'])

  return secret['client_id'], secret['client_secret'], secret['redirect_uri'], secret['refresh_token']
  
  
def retrieve_secret_prod():
  """
  Retrieves prod secret from AWS Secrets Manager (needed for Spotify OAuth).
  """
  secret_name = SECRET_NAME_PROD
  region_name = REGION_NAME

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
      raise e

  secret = json.loads(get_secret_value_response['SecretString'])

  return secret['client_id'], secret['client_secret'], secret['redirect_uri'], secret['refresh_token']
  
  
def write_to_s3_test():
  """Writes txt-file to S3 test bucket."""
  time_flag = datetime.today().strftime("%Y-%m-%d_%H-%M")
  bucket_name = DATA_BUCKET
  bucket_folders = f'{DATA_PREFIX}test/'
  
  file_name = f'{bucket_folders}test_file_{time_flag}.txt' 
  file_content = 'This is the content of the file.' 

  s3 = boto3.client('s3') 
  s3.put_object(Body=file_content, Bucket=bucket_name, Key=file_name)
  return { 
      'statusCode': 200, 
      'body': 'File uploaded successfully.' 
  }
  

def write_to_s3_prod():
  """Writes txt-file to S3 prod bucket."""
  time_flag = datetime.today().strftime("%Y-%m-%d_%H-%M")
  bucket_name = DATA_BUCKET
  bucket_folders = f'{DATA_PREFIX}prod/'
  
  file_name = f'{bucket_folders}test_file_{time_flag}.txt' 
  file_content = 'This is the content of the file.' 

  s3 = boto3.client('s3') 
  s3.put_object(Body=file_content, Bucket=bucket_name, Key=file_name)
  return { 
      'statusCode': 200, 
      'body': 'File uploaded successfully.' 
  }


def write_recently_played_user_tracks_to_s3(data: pd.DataFrame):
  """Writes recently palyed user tracks as csv-file to S3 prod bucket."""
  time_flag = datetime.today().strftime("%Y-%m-%d_%H-%M")
  bucket_name = DATA_BUCKET
  bucket_folders = f'{DATA_PREFIX}prod/'
  file_name = f'{bucket_folders}spotify_recently_played_tracks_{time_flag}.csv' 
  
  # Creates an in-memory text stream to hold the CSV content
  csv_buffer = StringIO()
  data.to_csv(csv_buffer, sep=';',index=False)
  
  # Uses in-memory text stream to store contents of 'data' in S3 as csv-file
  s3 = boto3.client('s3') 
  s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=file_name)


def update_refresh_token_in_secrets_manager_test(new_refresh_token: str):
  """Updates the refresh token stored in AWS Secrets Manager."""
  secret_name = SECRET_NAME_TEST
  
  # Create a Secrets Manager client
  session = boto3.session.Session()
  client = session.client(
      service_name='secretsmanager',
      region_name=REGION_NAME
  )

  # Get stored secret
  try:
      get_secret_value_response = client.get_secret_value(
          SecretId=secret_name
      )
  except ClientError as e:
      raise e

  secret = json.loads(get_secret_value_response['SecretString'])
  
  # Update the refresh token within the secret
  secret['refresh_token'] = new_refresh_token
  
  # Store the updated secret back to AWS Secrets Manager
  client.put_secret_value(
      SecretId=secret_name,
      SecretString=json.dumps(secret)
  )


def update_refresh_token_in_secrets_manager_prod(new_refresh_token: str):
  """Updates the refresh token stored in AWS Secrets Manager."""
  secret_name = SECRET_NAME_PROD
  
  # Create a Secrets Manager client
  session = boto3.session.Session()
  client = session.client(
      service_name='secretsmanager',
      region_name=REGION_NAME
  )

  # Get stored secret
  try:
      get_secret_value_response = client.get_secret_value(
          SecretId=secret_name
      )
  except ClientError as e:
      raise e

  secret = json.loads(get_secret_value_response['SecretString'])
  
  # Update the refresh token within the secret
  secret['refresh_token'] = new_refresh_token
  
  # Store the updated secret back to AWS Secrets Manager
  try:
    client.put_secret_value(
        SecretId=secret_name,
        SecretString=json.dumps(secret)
    )
  except ClientError as e:
        raise e

    
    