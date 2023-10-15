from utility import ec2
from utility import s3

number_of_instances = 1
print(ec2.create_ec2_instance(number_of_instances))
#print(s3.upload_s3_file('assets/website/index2.html','mahi2k'))
#print(s3.download_s3_file('index2.html','mahi2k'))
ec2.save_instance_details()