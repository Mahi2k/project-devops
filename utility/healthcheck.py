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
# Initialize clients
ec2 = boto3.client('ec2', region_name=region_name)
elbv2 = boto3.client('elbv2', region_name=region_name)
sns = boto3.client('sns', region_name=region_name)

def lambda_handler(event, context):
    # Get health of the target
    response = elbv2.describe_target_health(
        TargetGroupArn='arn:aws:elasticloadbalancing:ap-south-1:295397358094:targetgroup/group-8-target-group/85e7dac5fa5a9822'
    )
    
    for target in response['TargetHealthDescriptions']:
        # If any target is unhealthy
        if target['TargetHealth']['State'] == 'unhealthy':
            instance_id = target['Target']['Id']
            
            # Create snapshot
            ec2.create_snapshots(
                InstanceSpecification={
                    'InstanceId': instance_id,
                    'ExcludeBootVolume': False,
                    'Description':'This is my snapshot for ' + instance_id
                }
            )
            
            # Terminate the instance
            ec2.terminate_instances(
                InstanceIds=[instance_id]
            )
            
            # Send SNS notification
            sns.publish(
                TopicArn='arn:aws:sns:ap-south-1:295397358094:RamVenu_SNS',
                Message=f'Instance {instance_id} was unhealthy and has been terminated. A snapshot was created for debugging.',
                Subject='Unhealthy EC2 Instance Terminated'
            )