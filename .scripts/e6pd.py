#!/usr/bin/python3

import argparse
import base64
import configparser
import time
from urllib.parse import quote_plus
from urllib.request import urlretrieve
from pathlib import Path
from requests import get

# Read the arguments given to the script
parser = argparse.ArgumentParser(description="Download images from e621 from a tag or pool")
parser.add_argument("target", metavar="tag/pool", type=str, help="tag or pool to download (Ex: anthro, 11686)")
parser.add_argument("-t", "--title", type=str, help="set the title of the download set, for pools only")
parser.add_argument("-l", "--limit", type=int, help="set the limit for how many images to download, for tags only")
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

# Check if the target is a pool or tag, and URL encode it if it is a tag
is_pool = True
if not args.target.isnumeric():
    is_pool = False
    args.target = quote_plus(args.target)

# Ensure a title is given for a pool download
if is_pool and not args.title:
    print("A title is required when downloading a pool")
    exit()

# Print the collection status message
if args.title:
    print(f"[Collecting links for {args.title}]")
else:
    print(f"[Collecting links for {args.target}]")

# Fetch all post IDs in a pool, or iterate over every page for all post IDs in a tag
images = []
if is_pool:
    # Fetch post IDs directly into the pages array
    images = get(f"https://e621.net/pools/{args.target}.json", headers = headers).json()["post_ids"]
else:
    while True:
        if len(images) > 0:
            page = "b" + str(images[-1])
        else:
            page = ""

        # Fetch tag listings of a given page into a temp array
        temp = get(f"https://e621.net/posts.json?tags={args.target}&page={page}", headers = headers).json()["posts"]

        # Break when we have reached the last page
        if len(temp) == 0:
            break

        # Parse the post IDs into the main pages array
        for image in range(len(temp)):
            images.append(temp[image]["id"])

        # Cap the images found to the limit, if provided
        if args.limit and len(images) > args.limit:
            images = images[:args.limit]
            break

        print(f"Found {len(images)} links...")

        # Delay as to not spam API requests
        time.sleep(1)

# Create the required folder with the respective title, and print a status message
if args.title:
    print(f"[Started downloading {args.title} with {len(images)} images]")
    Path(args.title).mkdir(parents=True, exist_ok=True)
else:
    print(f"[Started downloading {args.target} with {len(images)} images]")
    Path(args.target).mkdir(parents=True, exist_ok=True)

# Download each image from the collected IDs
for image in range(len(images)):
    # Print a status message for each page
    print(f"Downloading page {str(image + 1)} of {str(len(images))}...")

    # Request the json file from the site
    request = get(f"https://e621.net/posts/{str(images[image])}.json", headers=headers).json()
    source = request["post"]["file"]["url"]
    time.sleep(1)

    # Title a tag or pool image with their respective naming convention
    if is_pool:
        img_path = Path.cwd() / args.title / f"{args.title} {str(image + 1).zfill(len(str(len(images))))}{Path(source).suffix}"
    else:
        artist = request["post"]["tags"]["artist"][0]
        img_path = Path.cwd() / args.target / f"{str(images[image])}__{artist}{Path(source).suffix}"

    # Write the image to disk
    urlretrieve(source, img_path)
    time.sleep(1)

# Print a final status when all downloads are finished
if args.title:
    print(f"[Finished downloading {args.title}]")
else:
    print(f"[Finished downloading {args.target}]")
