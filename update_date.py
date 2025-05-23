import subprocess

#sudo date MMDDhhmmYYYY

command = ["sudo","date", "052315262025"]

try:
    result = subprocess.run(command, check = True, capture_output=True, text=True)
    print("success:",result.stdout)
except subprocess.CalledProcessError as error:
    print("Error:", error.stderr)