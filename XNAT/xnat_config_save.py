#!/usr/bin/env python3
import requests
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--siteurl", required=True, help="Site URL (http[s]://<host>[:<port>])")
ap.add_argument("-u", "--user", required=True, help="Username")
ap.add_argument("-p", "--password", required=True, help="Password")
ap.add_argument("-f", "--configfile", required=True, help="Configuration json file")
ap.add_argument("--pp", action='store_true', help="Pretty-print to json file")

args = vars(ap.parse_args())

siteurl = args["siteurl"]
configfile = args["configfile"]
user = args["user"]
password = args["password"]
pp = args["pp"]

api_endpoint = siteurl.rstrip("/")+"/xapi/siteConfig"
headers = {"Content-Type": "application/json", "Accept": "*/*"}
    
try:
    response = requests.get(api_endpoint, headers=headers, auth=requests.auth.HTTPBasicAuth(user,password))
    response.raise_for_status()
except Exception as err:    
    print(f"Error occurred: {err}")
    exit(1)

data = json.dumps(response.json(), indent=4) if pp else response.text

try:
    open(configfile, "w").write(data)
except Exception as err:
    print(f"Can't write file: {err}")
    exit(1)
    
exit()
