#!/usr/bin/python3

import argparse
from pathlib import Path
from requests import get
from urllib.parse import unquote_plus

# Read the arguments given to the script
parser = argparse.ArgumentParser(description="Download images sets from yiffer.xyz")
parser.add_argument("target", metavar="url", type=str, help="target url to download")
parser.add_argument("length", metavar="length", type=int, help="set the number of images to download")
parser.add_argument("-t", "--title", type=str, help="set the title of the downloaded images")
args = parser.parse_args()

# Set the plain text name of the comic, file name, and the amount to pad numbers
comic_name = unquote_plus(args.target.split("/")[-1])
file_name = args.title if args.title else comic_name
padding = len(str(args.length))

# Print a status message, and create the required folder with an appropriate name
print(f"[Downloading {file_name} with {args.length} images]")
Path(file_name).mkdir(parents=True, exist_ok=True)

# Iterate until every image has been requested
for image_id in range(1, args.length + 1):
    # Send the request for the target url, and break if code 200 is not received
    image_data = get(f"{args.target.replace('yiffer.xyz', 'static.yiffer.xyz/comics')}/{image_id:03}.jpg")
    if image_data.status_code != 200: break

    # Print a status message for each page
    print(f"[Downloading image {image_id} of {args.length}]", end = "\r")

    # Set the appropriate image path to download to, then download it
    file_name = args.title if args.title else comic_name
    image_path = Path.cwd() / file_name / f"{file_name} {image_id:0{padding}}.jpg"
    with open(image_path, "wb") as image: image.write(image_data.content)

# Print a final status when all downloads are finished
print(f"\n[Finished {file_name}]")
