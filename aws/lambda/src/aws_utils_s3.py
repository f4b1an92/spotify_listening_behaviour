import boto3
from datetime import datetime
import pandas as pd
import logging

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def cleanup_s3_folder(s3_client: boto3.client, bucket_name: str, prefix: str, keep_last_x_files: int = 0) -> dict:
    """Cleans up folder in specified S3 bucket by removing all or all but the most recent file(s)."""    
    # List objects
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix
    )
    
    if response['KeyCount'] == 0:
        return {
            'statusCode': 200,
            'body': 'No files found in the S3 bucket to delete.'
        }
    else:
        if (keep_last_x_files == 0) & (response['KeyCount'] >= 1):
            # Delete each object
            for obj in response['Contents']:
                s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])  # no prefix needed here since obj already contains full path of the file
                logger.info(f"Deleted file: {obj['Key']}")
        elif (keep_last_x_files > 0) & (keep_last_x_files < (response['KeyCount']-1)):  # -1 to account for the folder itself
            # Delete each object except the most recent one's (which are defined by keep_last_x_files)
            meta_data_keys = []
            file_keys = []
            file_mod_times = []

            # Separate csv files (i.e. Athena query results) from meta data files
            for obj in response['Contents']:
                if obj['Key'].split('.')[-1] == 'csv':
                    file_keys.append(obj['Key'])
                    file_mod_times.append(obj['LastModified'])
                elif obj['Key'].split('.')[-1] == 'metadata':
                    meta_data_keys.append(obj['Key'])  # collect non-csv files (i.e. Athena metadata files) to delete them all later
                else:
                    pass  # do nothing for other file types (e.g. the encapsulating folder itself)
            relevant_file_df = pd.DataFrame({
                'file_key': file_keys,
                'mod_time': file_mod_times
            }).sort_values(by='mod_time', ascending=False).reset_index(drop=True)
            files_to_delete = relevant_file_df['file_key'][keep_last_x_files:].tolist()  # all but the most recent files (defined by keep_last_x_files)
            files_to_delete.extend(meta_data_keys)  # add all meta data files to the delete list as well

            # Now delete the files that are not needed anymore
            for obj in files_to_delete:
                s3_client.delete_object(Bucket=bucket_name, Key=obj)  # no prefix needed here since obj already contains full path of the file
                logger.info(f"Deleted file: {obj}")
        else:  
            # Delete nothing, since there only as many files as we want to keep in the folder (or less). Or in other words:
            # (keep_last_x_files > 0) & (keep_last_x_files >= response['KeyCount']-1): # with -1 to account for the folder itself
            return {
                'statusCode': 200,
                'body': f"We want to keep {keep_last_x_files} in the folder but only have {response['KeyCount']-1} atm. Thus nothing to delete."
            }
        return {
            'statusCode': 200,
            'body': f"Files deleted successfully from '{prefix.split('/')[-2]}' folder."
        }


def move_athena_query_results_to_archive(s3_client: boto3.client, bucket_name: str, prefix_query_results: str
                                         , prefix_archive: str) -> dict:
    """
    Moves most recent but outdated Athena query result file (e.g. from prev. day) from 'most_recent' 
    folder to 'archive' folder in S3.
    """
    time_flag = datetime.today().strftime("%Y-%m-%d_%H-%M")
  
    # List objects
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix_query_results
    )
    
    if response['KeyCount'] <= 1:
        return {
            'statusCode': 200,
            'body': 'Too few files found in the S3 bucket (0 or 1). No files copied to archive.'
        }
    else:
        # Extract file keys into a list
        file_keys = []
        file_mod_times = []
        for obj in response['Contents']: # each obj in response['Contents'] is a file in S3
            if obj['Key'].split('.')[-1] == 'csv':
                file_keys.append(obj['Key'])
                file_mod_times.append(obj['LastModified'])
        
        # Put all file keys and modification times into a dataframe to identify the most recent files    
        file_df = pd.DataFrame({
            'file_key': file_keys, 
            'mod_time': file_mod_times
        }).sort_values(
            by='mod_time', ascending=False
        ).reset_index(drop=True)
        most_recent_file = file_df.loc[1, 'file_key'] # use second row, since first row will contain the current file that was just written by Athena
        obj = s3_client.get_object(Bucket=bucket_name, Key=most_recent_file)
        df = pd.read_csv(obj['Body'],sep=',')
        
        # Convert DataFrame to CSV format in memory
        if prefix_archive.endswith('/'):
            file_name = f'{prefix_archive}athena_main_query_result_{time_flag}.csv' 
        else:
            file_name = f'{prefix_archive}/athena_main_query_result_{time_flag}.csv' 
        csv_buffer = df.to_csv(index=False)
        s3_client.put_object(Body=csv_buffer, Bucket=bucket_name, Key=file_name)
        return {
            'statusCode': 200,
            'body': 'File(s) copied to archive successfully.'
        }



