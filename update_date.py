import requests
import subprocess

url         = "https://dev-enmms-api.spphportal.site/api/get-date"
headers     = {
                "Authorization": "Bearer 3e13911adffce018d97286bb760dd49146d2a40318542bb1e99219a268f5340a%",
                "Content-Type": "application/json"
              }
response    = request.get(url, headers=headers)
data        = response.json()
print(data)

#sudo date MMDDhhmmYYYY
command = ["sudo","date", "052315262025"]

try:
    result = subprocess.run(command, check = True, capture_output=True, text=True)
    print("success:",result.stdout)
except subprocess.CalledProcessError as error:
    print("Error:", error.stderr)