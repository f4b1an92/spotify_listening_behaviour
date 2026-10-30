import os
from datetime import datetime
from functools import lru_cache

import pandas as pd

import src.dashboard_helpers.dashboard_utils as ut

APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = 'full_data_2026-10-26.csv'
SNAPSHOT_FILE = 'snapshot.csv'  # written into the public deploy folder by build_deploy_folder.py
SNAPSHOT_PATH = os.path.join(APP_ROOT, 'data', SNAPSHOT_FILE)
DEV_DATA_PATH = os.path.join(os.path.dirname(APP_ROOT), 'data', DATA_FILE)  # repo-level data/ folder

DEFAULT_S3_BUCKET = 'bucket-for-athena-outputs'
DEFAULT_S3_PREFIX = 'spotify-listening-behaviour/query_results_most_recent/'


def find_latest_csv_key(s3_client, bucket: str, prefix: str) -> str:
    """Return the key of the newest .csv object (by LastModified) under the prefix."""
    csv_objects = []
    for page in s3_client.get_paginator('list_objects_v2').paginate(Bucket=bucket, Prefix=prefix):
        csv_objects += [obj for obj in page.get('Contents', []) if obj['Key'].endswith('.csv')]
    if not csv_objects:
        raise FileNotFoundError(f's3://{bucket}/{prefix} contains no .csv file')
    return max(csv_objects, key=lambda obj: obj['LastModified'])['Key']


def read_csv_from_s3(bucket: str, prefix: str) -> pd.DataFrame:
    """Read the newest CSV under the S3 prefix; credentials and region come from the AWS_* env vars."""
    import boto3  # lazy: local runs without AWS settings don't need boto3

    s3_client = boto3.client('s3')
    key = find_latest_csv_key(s3_client, bucket, prefix)
    return pd.read_csv(s3_client.get_object(Bucket=bucket, Key=key)['Body'])


def has_aws_credentials() -> bool:
    """True when the app is configured to read the live pipeline output from S3."""
    return bool(os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'))


def read_raw_data() -> pd.DataFrame:
    """Read from S3 with AWS credentials, else from the bundled snapshot, else from the development CSV."""
    if has_aws_credentials():
        return read_csv_from_s3(
            bucket=os.environ.get('S3_BUCKET', DEFAULT_S3_BUCKET),
            prefix=os.environ.get('S3_PREFIX', DEFAULT_S3_PREFIX),
        )
    return pd.read_csv(SNAPSHOT_PATH if os.path.exists(SNAPSHOT_PATH) else DEV_DATA_PATH)


def get_latest_played_at(data: pd.DataFrame) -> datetime:
    """Return the timestamp of the most recent play, used instead of the wall-clock date."""
    return pd.to_datetime(data['played_at']).max().to_pydatetime()


def get_data_as_of_text(latest_played_at: datetime) -> str:
    """Header label: live S3 data is 'Data as of', anything read from a file is a 'Snapshot of'."""
    prefix = 'Data as of' if has_aws_credentials() else 'Snapshot of'
    return f"{prefix} {latest_played_at.strftime('%d.%m.%Y')}"


@lru_cache(maxsize=1)
def load_listening_data() -> pd.DataFrame:
    """Load and prepare the listening history once; the returned DataFrame is shared and must not be mutated."""
    data = read_raw_data()
    data = data.drop_duplicates(subset=['track_id', 'played_at']).reset_index(drop=True)
    data['played_at'] = pd.to_datetime(data['played_at'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')

    data = ut.fill_missing_features(data=data)
    data = ut.assign_main_genre(data=data)
    data = ut.assign_simplified_main_genre(data=data)

    data = ut.convert_track_duration(data=data)
    data = ut.add_fully_played_label(data=data, fully_played_threshold=0.95)
    return data
