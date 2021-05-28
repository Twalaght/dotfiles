#!/usr/bin/python3

from argparse import ArgumentParser
from base64 import b64encode
from configparser import ConfigParser
from multiprocessing import Pool, cpu_count
from pathlib import Path
from requests import get
from time import sleep
from urllib.parse import quote_plus
from urllib.request import urlretrieve

# Read the arguments given to the script
parser = ArgumentParser(description="Download images from e621 from a tag or pool")
parser.add_argument("target", metavar="tag/pool", type=str, help="tag or pool to download (Ex: anthro, 11686)")
parser.add_argument("-t", "--title", type=str, help="set the title of the download set, for pools only")
parser.add_argument("-l", "--limit", type=int, help="set the limit for how many images to download, for tags only")
args = parser.parse_args()

# Set up the config parser and read in the auths file
config = ConfigParser()
auths = Path.home() / ".config" / "auths.txt"
if auths.exists():
    config.read(auths)
else:
    print(f"Authentication not found at {auths}, please create it")
    exit()

# Calculate the b64_auth credential and set the request header
b64_auth = b64encode(f"{config.get('e621', 'user_name')}:{config.get('e621', 'API_key')}".encode("ascii")).decode("ascii")
headers = {"User-Agent": config.get("e621", "user_agent"), "Authorization": f"Basic {b64_auth}"}

# Check if target is a tag or pool
is_pool = True if args.target.isnumeric() else False

# Set a default title if no title is provided
if not args.title: args.title = get(f"https://e621.net/pools/{args.target}.json", headers = headers).json()["name"].replace("_", " ") if is_pool else args.target

# URL encode the target so it can be used for API requests
args.target = quote_plus(f"pool:{args.target}") if is_pool else quote_plus(args.target)

# Print the initial status message
print(f"[Preparing {args.title}]")

# Iterate until IDs and URLs are found for every post
images = []
while True:
    # Set the page number on every request past the first one
    page = f"b{images[-1][0]}" if len(images) > 0 else ""

    # Request the list of posts through the API
    posts = get(f"https://e621.net/posts.json?limit=320&tags={args.target}&page={page}", headers = headers).json()["posts"]

    # Parse each post into their respective arrays, with image ID, full size URL, and artist name
    for post in posts: images.append([post["id"], post["file"]["url"], post["tags"]["artist"][0].replace("_(artist)", "")])

    # Limit the parsed posts to that of the limit argument
    if args.limit and len(images) >= args.limit:
        images = images[:args.limit]
        break

    # If a set of posts did not reach the requested size, it was the final set
    if len(posts) < 320: break

    # Delay requests to ensure the proper rate limit to the API
    sleep(1)

# Download pools in reverse upload order
if is_pool: images.reverse()

# Create the required folder with the respective title, and print a status message
print(f"[Downloading {args.title} with {len(images)} posts]")
Path(args.title).mkdir(parents=True, exist_ok=True)

# Download an image from a tuple of arguments
def download_image(image_url, image_path, index):
    # Print status messages over each other, and retrieve the image to disk
    print(f"[Downloading image {index} of {len(images)}]", end = "\r")
    urlretrieve(image_url, image_path)

# Create an entry in the download argument list for each post
download_args = []
for image in range(len(images)):
    # Set an images download path with the respective naming convention
    padding = len(str(len(images)))
    extension = Path(images[image][1]).suffix
    if is_pool: img_path = Path.cwd() / args.title / f"{args.title} {str(image + 1).zfill(padding)}{extension}"
    if not is_pool: img_path = Path.cwd() / args.title / f"{str(images[image][0])}__{images[image][2]}{extension}"
    download_args.append((images[image][1], img_path, image + 1))

# Create a pool of threads, and use them to download images in parallel
Pool(cpu_count()).starmap(download_image, download_args, chunksize = 1)

# Print a final status when all downloads are finished
print(f"\n[Finished {args.title}]")
