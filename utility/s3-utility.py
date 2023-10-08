import logging
import boto3
import os
from botocore.exceptions import ClientError

def get_boto3_s3_client():
    s3 = boto3.client('s3')
    return s3

def create_new_s3_bucket(bucket_name):
    # Create bucket
    try:
        s3_client = get_boto3_s3_client()
        s3_client.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def list_all_s3_buckets():
    # Retrieve the list of existing buckets
    s3_client = get_boto3_s3_client()
    response = s3_client.list_buckets()
    
    # Output the bucket names
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')

    return response['Buckets']


def upload_s3_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        s3_client = get_boto3_s3_client()
        with open("FILE_NAME", "rb") as f:
            file = s3_client.upload_fileobj(f, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def download_s3_file(fileName, bucketName, objectName):
    s3_client = get_boto3_s3_client()
    with open(fileName, 'wb') as f:
        s3_client.download_fileobj(bucketName, objectName, f)