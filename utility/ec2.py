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

# Read the ec2 details file for the data that is already present
ec2_instance_data = file_operations.readJsonFile(ec2_details_path)

aws_mgmt_console = boto3.session.Session(profile_name=profile_name)
ec2_client = boto3.client("ec2", region_name=region_name)

# Function for creating an instance
def create_ec2_instance(numberOfInstance, minCount = 1, maxCount = 1):
    try:
        for i in range(numberOfInstance):
            instances = ec2_client.run_instances(
                ImageId=ami_id,
                MinCount=1,
                MaxCount=1,
                InstanceType=instance_type,
                KeyName=key_pair,
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": key_pair_name + "-" + str(i)
                            },
                        ]
                    },
                ]
            )
            instance_id = instances["Instances"][0]["InstanceId"]
            
            # Update the list of ec2 instance id's and save it
            if "ec2_instance_list" in ec2_instance_data:
                ec2_instance_data["ec2_instance_list"].append(instance_id)
            else:
                ec2_instance_data["ec2_instance_list"] = [instance_id]
                
        # Save the data into the ec2_details file
        file_operations.saveJsonFile(ec2_details_path, ec2_instance_data)
        logging.info(msg="New group8 instance created: " + instance_id)
        return True
    except ClientError as e:
        logging.error(e)
        return False

def save_instance_details(instance_id = None):
    filterParams =[{
                    "Name":"instance-state-name",
                    "Values":["running"]    
                }]
    
    try:
        reservation_object = ec2_client.describe_instances(
            Filters = filterParams,
            InstanceIds=[instance_id]
            ).get("Reservations")

        # Loop through reservation to get instances and also there public ip
        for reservation in reservation_object:
            for instance in reservation["Instances"]:
                public_ip = instance.get("PublicIpAddress")
                print(public_ip)
            # Update the list of ec2 instance id's and save it
            if "ec2_instance_ip" in ec2_instance_data:
                ec2_instance_data["ec2_instance_ip"].append(instance_id + "|" + str(public_ip))
            else:
                ec2_instance_data["ec2_instance_ip"] = [instance_id + "|" + str(public_ip)]
                
        # Save the data into the ec2_details file
        file_operations.saveJsonFile(ec2_details_path, ec2_instance_data)
        return True
    except ClientError as e:
        logging.error(e)
        return False
    
# def terminate_all_instances():
#     ec2_data = file_operations.readJsonFile(ec2_details_path)
    
#     for data in ec2_data:
#         data["instance_id"]