#!/usr/bin/env python3

import argparse
from pathlib import Path
from requests import get
from urllib.parse import unquote_plus

# Read the arguments given to the script
parser = argparse.ArgumentParser(description="Download images sets from yiffer.xyz")
parser.add_argument("target", metavar="url", type=str, help="target url to download")
parser.add_argument("-t", "--title", type=str, help="set the title of the downloaded images")
args = parser.parse_args()

# Set the first image, the URL encoded name, and the regular name
image_id = 1
name = args.target.split("/")[-1]
comic_name = unquote_plus(name)

# Create the required folder with the title if provided, or the comic name
if args.title:
    print(f"[Starting download for {args.title}]")
    Path(args.title).mkdir(parents=True, exist_ok=True)
else:
    print(f"[Starting download for {comic_name}]")
    Path(comic_name).mkdir(parents=True, exist_ok=True)

# Iterate until every image has been requested
while True:
    name = args.target.split("/")[-1]
    page = "{0:02d}.jpg".format(image_id)
    source = f"{args.target}/../comics/{name}/{page}"

    # Send the request for the target url, and break if code 200 is not received
    image_data = get(source)
    if image_data.status_code != 200:
        break

    # Print a status message for each page
    print(f"Downloading page {image_id}...")

    # Set the appropriate image path to download to, then download it
    if args.title:
        image_path = Path.cwd() / args.title / f"{args.title} {page}"
    else:
        image_path = Path.cwd() / comic_name / f"{comic_name} {page}"

    with open(image_path, "wb") as image:
        image.write(image_data.content)

    # Increase the page number and keep downloading
    image_id = image_id + 1

# Print a final status when all downloads are finished
if args.title:
    print(f"[Finished downloading {args.title}]")
else:
    print(f"[Finished downloading {comic_name}]")
