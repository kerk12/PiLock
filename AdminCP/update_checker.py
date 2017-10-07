from urllib import urlopen
import requests
import subprocess

class UpdateCheckError(Exception):
    pass

def check_for_updates():
    url = "https://api.github.com/repos/kerk12/PiLock/git/refs/heads/master"
    req = requests.get(url)

    if req.status_code != 200:
        raise UpdateCheckError("Origin unreachable.")

    sha_origin = req.json()["object"]["sha"][:7]
    sha_local = subprocess.check_output(["git", "describe", "--always"]).strip()

    return sha_local != sha_origin