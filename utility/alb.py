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

#Create an application load balancer
def create_load_balancer():
    elb_client = boto3.client('elbv2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    
    response = elb_client.create_load_balancer(
        Name = 'group-8-alb',
        Subnets=['subnet-054d138c719f3f355','subnet-0ea24e054cba9cad2','subnet-0ea185273ead71a27'],
        SecurityGroups=['sg-0103a917e74448c29'],
        Scheme='internet-facing',
        Tags=[{
            'Key':'Name',
            'Value':'group-8-alb'
        },],
        Type='application',
        IpAddressType='ipv4'
    )

    #Get the ARN of newly created application load balancer
    load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    print(f"Application Load Balancer with ARN {load_balancer_arn} has been created.")

    #Create Target Group
    response = elb_client.create_target_group(
        Name='group-8-targetgroup',
        Protocol='HTTP',
        Port=80,
        VpcId='vpc-0c5a8881cff1146d8',
        TargetType='instance',  # Set to 'ip' if you are using IP addresses as targets
        HealthCheckProtocol='HTTP', # Health check protocol, can be 'HTTP', 'HTTPS', 'TCP', or 'UDP'
        HealthCheckPort='80', # Port used for health checks
        HealthCheckPath='/', # Path used for health checks
        HealthCheckIntervalSeconds=30, # Interval between health checks
        HealthCheckTimeoutSeconds=5, # Timeout for health checks
        HealthyThresholdCount=2, # Number of consecutive successful health checks required
        UnhealthyThresholdCount=2,  # Number of consecutive failed health checks required
        Matcher={
            'HttpCode': '200'
        },
    )

    # Get the ARN of the newly created Target Group
    target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
    print(f"Target Group with ARN {target_group_arn} has been created.")

    # Register a target (EC2 instance) with the Target Group
    instance_ids = ec2_instance_data
    targets = [{'Id': i} for i in instance_ids]
    response = elb_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=targets
    )

    # Create a listener for the Load Balancer that forwards HTTP traffic to the Target Group
    response = elb_client.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_arn,
            },
        ]
    )

    #Configure the ALB to send access logs to the S3 bucket.
    elb_client.modify_load_balancer_attributes(
    LoadBalancerArn=load_balancer_arn,
    Attributes=[
        {
            'Key': 'access_logs.s3.enabled',
            'Value': 'true'
        },
        {
            'Key': 'access_logs.s3.bucket',
            'Value': 'mahi2k'
        },
        {
            'Key': 'access_logs.s3.prefix',
            'Value': 'my-load-balancer-logs'
        }
    ]
)
    return target_group_arn, ec2_instance_data[0]

#create_load_balancer()