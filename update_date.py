import configuration
import requests
import subprocess

api_link    = configuration.api_link
api_bearer  = configuration.api_bearer

url         = f"""{api_link}/api/get-date"""
headers     = {
                "Authorization": api_bearer,
                "Content-Type": "application/json"
              }
response    = requests.get(url, headers=headers)
data        = response.json()
current_date= data["date"]    

#sudo date MMDDhhmmYYYY
command = ["sudo","date", current_date]

try:
    result = subprocess.run(command, check = True, capture_output=True, text=True)
    print("success:",result.stdout)
except subprocess.CalledProcessError as error:
    print("Error:", error.stderr)