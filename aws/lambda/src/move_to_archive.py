import json
import boto3
from datetime import datetime
import pandas as pd
import os
import logging
import aws_utils_s3 as aut

FILES_TO_KEEP = 5
ATHENA_BUCKET = os.environ.get('SPOTIFY_ATHENA_BUCKET', 'bucket-for-athena-outputs')
PREFIX_QUERY_RESULTS = os.environ.get('SPOTIFY_ATHENA_PREFIX_MOST_RECENT', 'spotify-listening-behaviour/query_results_most_recent/')
PREFIX_ARCHIVE = os.environ.get('SPOTIFY_ATHENA_PREFIX_ARCHIVE', 'spotify-listening-behaviour/query_results_archive/')

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize S3 client and define bucket and prefixes
    s3_client = boto3.client('s3')
    bucket_name = ATHENA_BUCKET
    prefix_query_results = PREFIX_QUERY_RESULTS
    prefix_archive = PREFIX_ARCHIVE

    # Moves most recent Athena query result from prev. days to archive (i.e. the file
    # just created by Athena remains in 'most_recent' folder).
    move_response = aut.move_athena_query_results_to_archive(
        s3_client=s3_client, 
        bucket_name=bucket_name, 
        prefix_query_results=prefix_query_results,
        prefix_archive=prefix_archive
    )
    logger.info(move_response['body'])
    
    # Clean up 'most_recent' folder by deleting all but the file that was just created by Athena
    cleanup_response = aut.cleanup_s3_folder(
        s3_client=s3_client, 
        bucket_name=bucket_name, 
        prefix=prefix_query_results,
        keep_last_x_files=1  # keep the most recent file (i.e. the one just created by Athena)
    )
    logger.info(cleanup_response['body'])

    # Cleanup 'archive' folder by deleting all but the most recent 5 files
    cleanup_response_archive = aut.cleanup_s3_folder(
        s3_client=s3_client, 
        bucket_name=bucket_name, 
        prefix=prefix_archive,
        keep_last_x_files=FILES_TO_KEEP  # number of files to keep in archive
    )
    logger.info(cleanup_response_archive['body'])

    return {
        'statusCode': 200,
        'body': 'Athena query results moved to archive and S3 folders cleaned up successfully.'
    }
