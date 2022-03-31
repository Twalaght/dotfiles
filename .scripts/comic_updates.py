#!/usr/bin/python3

from base64 import b64encode
from configparser import ConfigParser
from json import load
from os import getenv
from pathlib import Path
from requests import get
from time import sleep

# Set the base directory from the environment variable
base_dir = getenv("COMIC_PATH")
if base_dir:
	base_dir = Path(base_dir)
else:
	print(f"No comic path environment variable, please set it")
	exit()

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

# Read in the watchlist file
with open(base_dir / "watchlist.json") as f: watchlist = load(f)

# For each comic in the watchlist check its local data against the server
for comic in watchlist["comics"]:
	# Count how many local files we have
	local_num = comic["offset"]
	for page in Path(base_dir / comic["folder"]).iterdir():
		if page.is_file(): local_num += 1

	# Query the server for total number of files, and get the name too
	server_num = get(f"https://e621.net/pools/{comic['id']}.json", headers = headers).json()["post_count"]

	if local_num < server_num:
		print(f"* {comic['name']} has {server_num - local_num} new pages")
	elif local_num > server_num:
		print(f"\033[34m{comic['name']} is ahead of e6 by {local_num - server_num} pages\033[0m")
	else:
		print(f"\033[32m{comic['name']} is up to date\033[0m")

	sleep(1)
