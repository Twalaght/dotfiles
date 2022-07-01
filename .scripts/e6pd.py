#!/usr/bin/python3

from argparse import ArgumentParser
from base64 import b64encode
from configparser import ConfigParser
from multiprocessing import Pool, cpu_count
from os import getenv
from pathlib import Path
from requests import get
from time import sleep
from urllib.parse import quote_plus
from urllib.request import URLopener

# Generate a request header from configuration file
def gen_headers():
	# Ensure the config environment variable is set
	auth_path = getenv("AUTH_PATH")
	if auth_path is None:
		print(f"Error - AUTH_PATH environment variable is not set")
		exit(1)

	# Initialise the config parser and ensure e621 information is present
	config = ConfigParser()
	config.read(Path(auth_path))
	if "e621" not in config:
		print(f"Error - e621 segment not found in config, example template below")
		print("[e621]\nuser_agent:\nuser_name:\nAPI_key:")
		exit(1)

	# Calculate the base 64 credential and return the full request header
	e621 = config["e621"]
	b64_auth = f"{e621['user_name']}:{e621['API_key']}"
	b64_auth = b64encode(b64_auth.encode("ascii")).decode("ascii")
	return {"User-Agent": e621["user_agent"], "Authorization": f"Basic {b64_auth}"}

# Collect post information from e621 based on the search queries
def get_images(target, offset, limit, pool, headers):
	# Set the search target, dependent on the type of search
	search = f"pool:{target}" if pool else quote_plus(target)

	images = []
	while True:
		# Set the show after image on every request, except for the first
		page = f"b{images[-1][0]}" if len(images) > 0 else ""

		# Request each page of posts from e621 through the API
		base_url = "https://e621.net/posts.json?limit=320"
		posts = get(f"{base_url}&tags={search}&page={page}", headers = headers).json()["posts"]

		# Process each post, set the artist name as needed, and at it to the image list
		for post in posts:
			img_id = post["id"]
			source = post["file"]["url"]
			if post["tags"]["artist"]:
				artist = post["tags"]["artist"][-1].replace("_(artist)", "")
			else:
				artist = "unknown_artist"

			images.append([img_id, source, artist])

		# Break if either the last page of the search or the image limit is reached
		if len(posts) < 320: break
		if limit and len(images) >= limit and not pool: break

		# Delay requests to ensure rate limiting for API calls
		sleep(1)

	# If the target is a pool, use the pool info to enforce image order
	if pool:
		pool_info = get(f"https://e621.net/pools/{target}.json", headers = headers).json()
		target = pool_info["name"].replace("_", " ")
		posts = pool_info["post_ids"]

		# Remove deleted items from the pool
		posts = [x for x in pool_info["post_ids"] if x in [i[0] for i in images]]

		# Match the images to the correct order stated by the pool
		images = [next(x for x in images if x[0] == post) for post in posts]

	# Set the limit to include offset if needed, return images and search name
	if limit and offset: limit += offset
	return images[offset:limit], target

# Create an entry in the download argument list for each post
def gen_download_args(images, title, folder, offset, n_offset, pool):
	# Set the base download path if provided, otherwise use the title
	base = Path(folder) if folder else Path.cwd() / title

	# Iterate through the set of collected image data
	download_args = []
	for i in range(len(images)):
		# Extract the extension of each image
		ext = images[i][1].split(".")[-1]

		# Generate the download path for each image
		if pool:
			combined = (offset if offset else 0) + (n_offset if n_offset else 0)
			# Determine numbering and padding for pools, and set image path
			img_num = i + 1 + combined
			zero_len = len(str(len(images) + combined))
			pad = f"0{max(zero_len, 2)}"
			img_path = base / f"{title} {format(img_num, pad)}.{ext}"
		else:
			# For regular searches, save the image with ID and artist name
			img_path = base / f"{images[i][0]}__{images[i][2]}.{ext}"

		# Append each argument to the list
		download_args.append((images[i][1], img_path, i + 1, len(images)))

	return download_args

# Download files from a download argument tuple
def parallel_download(url, path, index, length):
	# Print status messages as files are downloaded
	closer = f"/{length}" if length else ""
	print(f"[Downloading - {index}{closer}]", end = "\r")

	# Download the specified file
	opener = URLopener()
	opener.addheader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36")
	opener.retrieve(url, path)

# Download the image set with the given arguments
def e6pd(target, title, offset, n_offset, limit, folder, pool, headers):
	# Get a set of posts for either a seach query or a pool
	print(f"[Preparing {target}]")
	images, name = get_images(target, offset, limit, pool, headers)

	# Set a title if one was not provided, and sanitise for file paths
	if not title:
		title = name if pool else args.target
		title.replace("_" if pool else ":", " " if pool else "")
		title = "".join(x for x in title if x not in list("\\/:*?\"<>|"))

	# Create the required folder with the respective title, and print a status message
	target_folder = folder if folder else title
	Path(target_folder).mkdir(parents = True, exist_ok = True)
	print(f"[Downloading {title} with {len(images)} posts]")

	# Generate a tuple of arguments that can be downloaded in parallel
	download_args = gen_download_args(images, title, folder, offset, n_offset, pool)

	# Create a pool of threads, and use them to download in parallel
	Pool(cpu_count()).starmap(parallel_download, download_args, chunksize = 1)

	# Print a final status when all downloads are finished
	print(f"\n[Finished {title}]")

if __name__ == "__main__":
	# Read the arguments given to the script
	parser = ArgumentParser(description="Download images from e621 from a search query or pool")
	parser.add_argument("target", metavar="search/pool", type=str, help="search or pool to download (Ex: anthro canine, 11686)")
	parser.add_argument("-t", "--title", type=str, help="for pools only, set the title of the download set")
	parser.add_argument("-l", "--limit", type=int, help="limit the number of images to download")
	parser.add_argument("-o", "--offset", type=int, help="offset which post to start downloading from")
	parser.add_argument("-n", "--noffset", type=int, help="naming offset, should only be used in scripts")
	parser.add_argument("-f", "--folder", type=str, help="download to a specified folder")
	args = parser.parse_args()

	# Determine if the target is a pool, generate headers, then download the set
	pool = args.target.isnumeric()
	headers = gen_headers()
	e6pd(args.target, args.title, args.offset, args.noffset, args.limit, args.folder, pool, headers)
