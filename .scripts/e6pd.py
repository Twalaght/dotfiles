#!/usr/bin/python3

import argparse
import base64
import configparser
import time
import urllib.request
from pathlib import Path
from requests import get

# Read the arguments given to the script
parser = argparse.ArgumentParser(description="Download a pool of images from e621")
parser.add_argument("pool_id", metavar="pool_ID", type=str, help="Pool of images to download (Ex: 11686)")
parser.add_argument("name", metavar="name", type=str, help="Name template to use when saving the images")
args = parser.parse_args()

# Set up the config parser and read in the auths file if it exists
config = configparser.ConfigParser()
auths = Path.home() / ".config" / "auths.txt"
if auths.exists():
    config.read(auths)
else:
    print(f"Authentication not found at {auths}, please create it")
    exit()

# Set all relevant configuration variables
user_agent = config.get("e621", "user_agent")
user_name = config.get("e621", "user_name")
API_key = config.get("e621", "API_key")

# Calculate the basic auth b64 credential and set the required request header
user_auth = (user_name + ":" + API_key).encode("ascii")
b64_auth = "Basic " + base64.b64encode(user_auth).decode("ascii")
headers = {"User-Agent": user_agent, "Authorization": b64_auth}

# Get all the post IDs belonging to the pool
pages = get(f"https://e621.net/pools/{args.pool_id}.json", headers=headers).json()["post_ids"]
time.sleep(1.5)

# Create the required folder with the given name
Path(args.name).mkdir(parents=True, exist_ok=True)

# Print an opening status message for the pool
print(f"[Started downloading {args.name}]")

# Download each page in the pool
for page in range(len(pages)):
    # Print a status message for each page
    print(f"Downloading page {str(page + 1)} of {str(len(pages))}...")

    # Get the source for each individual image
    image = get(f"https://e621.net/posts/{str(pages[page])}.json", headers=headers).json()["post"]["file"]["url"]
    time.sleep(1.5)

    # Generate the file path for each image to be saved to
    img_path = Path.cwd() / args.name / (args.name + " " + str(page + 1).zfill(len(str(len(pages)))) + Path(image).suffix)

    # Write the image to disk
    urllib.request.urlretrieve(image, img_path)
    time.sleep(1.5)

# Print a final status when all downloads are finished
print(f"[Finished downloading {args.name}]")
