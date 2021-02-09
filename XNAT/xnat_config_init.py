#!/usr/local/bin/python3
import requests
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--siteurl", required=True, help="Site URL")
ap.add_argument("-u", "--user", required=True, help="Username")
ap.add_argument("-p", "--password", required=True, help="Password")
ap.add_argument("-f", "--configfile", required=True, help="Configuration json file")

args = vars(ap.parse_args())

siteurl = args["siteurl"]
configfile = args["configfile"]
user = args["user"]
password = args["password"]

api_endpoint = "https://"+siteurl+"/xapi/siteConfig"
headers = {"Content-Type": "application/json", "Accept": "*/*"}
try:
    data = open(configfile, "r").read()
except Exception as err:
    print(f"Can't read file: {err}")
    exit(1)
    
try:
    response = requests.post(api_endpoint, data=data, headers=headers, auth=requests.auth.HTTPBasicAuth(user,password))
    response.raise_for_status()
except Exception as err:    
    print(f"Error occurred: {err}")
    exit(1)
    
exit()
