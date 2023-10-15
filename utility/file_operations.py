import json
import os

# Function for reading the json data file
def readJsonFile(file_path):
    returningJson = {}
    if os.path.exists(file_path):
        try:
            f = open(file_path, 'r')
            returningJson = json.load(f)
            f.close()
            return returningJson
        except ValueError:
            print("Decode error")
            return returningJson
    else:
        return returningJson

#print(readJsonFile("assets/data/ec2_config.json"))
#print(readJsonFile("assets/data/ec2_details.json"))

# Function for dumping data to the json file    
def saveJsonFile(file_path, data): 
    jsonString = json.dumps(data)
    f = open(file_path, 'w')
    f.write(jsonString)
    f.close()
        