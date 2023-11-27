import boto3, time
import logging
import boto3
from utility import file_operations
from botocore.exceptions import ClientError

# Read config json file for EC2
ec2_config_path = "assets/config/ec2_config.json"
ec2_config = file_operations.readJsonFile(ec2_config_path)

ami_id = ec2_config["instance_ami_id"]
region_name = ec2_config["aws_region"]
key_pair = ec2_config["key_pair"]
key_pair_name = ec2_config["key_pair_name"]
profile_name = ec2_config["profile_name"]
instance_type = ec2_config["instance_type"]
ec2_details_path = ec2_config["ec2_details_path"]

aws_access_key_id = ec2_config['aws_access_key_id']
aws_secret_access_key = ec2_config['aws_secret_access_key']

# Read the ec2 details file for the data that is already present
ec2_instance_data = file_operations.readJsonFile(ec2_details_path)

aws_mgmt_console = boto3.session.Session(profile_name=profile_name)
time.sleep(200)
# Initialize the S3 and SNS clients
s3 = boto3.client('s3', region_name=region_name)
sns = boto3.client('sns', region_name=region_name)

def lambda_handler(event, context):
    # Get the bucket name and file key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Get the log file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    log_file_content = response['Body'].read().decode('utf-8')
    
    # Analyze the log file (this is just a placeholder - replace with your own log analysis)
    log_data = json.loads(log_file_content)
    if 'suspicious_activity' in log_data:
        # If suspicious activity is found, send an SNS notification
        sns.publish(
            TopicArn='arn:aws:sns:ap-south-1:295397358094:group-8-sns',
            Message='Suspicious activity detected in log file: ' + key,
            Subject='Suspicious Activity Detected'
        )