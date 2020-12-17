#!/usr/bin/python3

import argparse
import base64
import configparser
import hashlib
import os
import re
import time
from pathlib import Path
from requests import get

# Read the arguments given to the script
parser = argparse.ArgumentParser(description="Rename local images to e621 post number and artist")
parser.add_argument("-r", action="store_true", help="Search for images recursively")
args = parser.parse_args()

# Set up the config parser and read in the auths file if it exists
config = configparser.ConfigParser()
auths = Path.home() / ".config" / "auths.txt"
if auths.exists():
    config.read(auths)
else:
    print(f"Authentication not found at {auths}, please create it")

# Set all relevant configuration variables
user_agent = config.get("e621", "user_agent")
user_name = config.get("e621", "user_name")
API_key = config.get("e621", "API_key")

# Calculate the basic auth b64 credential and set the required request header
user_auth = (user_name + ":" + API_key).encode("ascii")
b64_auth = "Basic " + base64.b64encode(user_auth).decode("ascii")
headers = {"User-Agent": user_agent, "Authorization": b64_auth}

# Walk through the working directory and find each image
images = []
for path, subdir, files in os.walk(Path.cwd()):
    for file in files:
        # Ignore any files that are not images
        if os.path.splitext(file)[1] not in [".png", ".PNG", ".jpeg", ".JPEG", ".jpg", ".JPG"]:
            continue

        # Ignore subfolders if the recursive flag is not given
        if not args.r and Path(path) != Path.cwd():
            continue

        # Ignore files which already have been named
        if re.match("^[0-9]+__", file):
            continue

        # Append the full path of the file to the image list
        images.append(Path(path) / file)

# Return the MD5 hash for a given file
def hash(image):
    with open(image, "rb") as file:
        file_hash = hashlib.md5()
        file_hash.update(file.read())

    return file_hash.hexdigest()

# For each valid image, hash, search, and rename them
for image in images:
    # Search for a valid image from the hash
    search = get(f"https://e621.net/posts.json?tags=md5%3A{hash(image)}", headers=headers).json()["posts"]
    time.sleep(1.5)

    # If no valid image is found, print a message and continue to the next one
    if not search:
        print(f"*** [No e621 entry found for {image}] ***")
        continue

    # Print a status message
    print(f"[Renaming {image}]")

    # Create the name in the format "post-id__artist"
    new_name = str(search[0]["id"]) + "__" + search[0]["tags"]["artist"][0]
    new_name = re.sub("[^/]*?\.", new_name + ".", str(image))

    # Rename the file with the newly generated name
    os.rename(image, new_name)
