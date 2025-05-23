import configuration
import requests
import subprocess

api_link    = configuration.url_link
url         = f"""{api_link}/api/get-date"""
headers     = {
                "Authorization": "Bearer 3e13911adffce018d97286bb760dd49146d2a40318542bb1e99219a268f5340a%",
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