import boto3, time
from alb import create_load_balancer
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

resultALB = list(create_load_balancer())
target_grp_arn = resultALB[0]
instance_id = resultALB[1]

time.sleep(200)

#Create an Auto scaling group
def create_auto_scaling_group():
    autoscaling = boto3.client('autoscaling', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region)
    
# Create launch configuration
    autoscaling.create_launch_configuration(
        LaunchConfigurationName='group-8-launch-template',
        InstanceId=instance_id,
    )
    print("Lauch Template created successfully.")

# Create auto scaling group
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='group-8-asg',
        LaunchConfigurationName='group-8-launch-template',
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=1,
        LoadBalancerTargetGroupConfigurations=[
        {
            'TargetGroupArn': target_grp_arn,
        },
    ],
        VPCZoneIdentifier='subnet-054d138c719f3f355, subnet-0ea24e054cba9cad2, subnet-0ea185273ead71a27',
    )
    print("ASG created successfully.")

# Create scale out policy
    scale_out_policy = autoscaling.put_scaling_policy(
        AutoScalingGroupName='group-8-asg',
        PolicyName='Grp7_SCALE_OUT_POLICY',
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
               'PredefinedMetricType': 'ASGAverageCPUUtilization',
            },
            'TargetValue': 20.0,
        }
    )
    print("Scale OUT policy created successfully.")

create_auto_scaling_group()