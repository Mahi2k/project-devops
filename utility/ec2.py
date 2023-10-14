import logging
import boto3
from botocore.exceptions import ClientError


init_script="""#!/bin/bash
    sudo apt-get update -y
    sudo apt-get install nginx -y
    sudo systemctl reload nginx   
    """
def create_ec2_instance(ami_id = 'ami-0f5ee92e2d63afc18'):
    try:
        aws_mgmt_console = boto3.session.Session(profile_name='default')
        ec2 = aws_mgmt_console.client('ec2')
        
        instances = ec2.run_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            KeyName="group8-boto-keypair",
            UserData=init_script,
            TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'boto3-group8'
                    },
                ]
            },
            ]  
        )
        instance_id = instances['Instances'][0]['InstanceId']
        logging.info(msg="Group8 InstanceId: " + instance_id)
        return instance_id

    except ClientError as e:
        logging.error(e)
        return 'Error: Error occuerred while creating instance'
