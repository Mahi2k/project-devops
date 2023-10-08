import logging
import boto3
import os
from botocore.exceptions import ClientError

def create_ec2_instance(ami_id = 'ami-0f5ee92e2d63afc18'):
    
    aws_mgmt_console = boto3.session.Session(profile_name='default')
    ec2 = aws_mgmt_console.client('ec2')
    
    instances = ec2.run_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="group8-boto-keypair"
    )
    print(instances)



create_ec2_instance()