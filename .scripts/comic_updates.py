#!/usr/bin/python3

from argparse import ArgumentParser
from e6pd import gen_headers, e6pd, parallel_download
from os import getenv
from pathlib import Path
from requests import get
from time import sleep
import json

# Read and verify the base directory and database file
def setup():
	# Read the base directory from the environment variable
	base_dir = getenv("COMIC_PATH")
	if base_dir is None:
		print("Error - COMIC_PATH environment variable is not set")
		exit(1)

	# Set the base directory and read in the database file
	base_dir = Path(base_dir)
	comic_database = base_dir / "comics.json"
	if not comic_database.exists():
		print(f"Error - {comic_database} does not exist")
		exit(1)

	with open(base_dir / "comics.json") as f:
		comics = json.load(f)

	# Sort the ongoing entries and return the data
	comics["ongoing"].sort(key = lambda x: x["name"])
	return base_dir, comics

# Download new comic pages hosted on e621
def download_updates(base_dir, comics):
	headers = gen_headers()
	for comic in comics:
		# Ensure the target comic folder exists
		if not (base_dir / comic["name"]).exists():
			print(f"WARNING - Folder {base_dir / comic['name']} does not exist")
			continue

		# Count how many local files we have, with an offset included
		local_num = -comic["offset"]
		for page in (base_dir / comic["name"]).iterdir():
			if page.is_file(): local_num += 1

		# Query e621 to find how many pages are listed
		server_num = get(f"https://e621.net/pools/{comic['id']}.json", headers = headers).json()["post_count"]

		# Download the new pages if the server has more than local
		if local_num < server_num:
			print(f"* {comic['name']} has {server_num - local_num} new pages")

			# If the update flag is set, update the comic
			if comic["update"]:
				# Set the offsets corresponding to deleted posts or combined pools
				n_offset = comic["offset"] if comic["offset"] > 0 else None
				if comic["offset"] < 0: local_num += comic["offset"]

				# Set the download folder and download the required pages
				dl_folder = base_dir / comic["name"]
				e6pd(comic["id"], comic["name"], local_num, n_offset, None, dl_folder, True, headers)

		# Report if the comic is ahead or matching the server
		elif local_num > server_num:
			print(f"\033[34m{comic['name']} is ahead of e6 by {local_num - server_num} pages\033[0m")
		else:
			print(f"\033[32m{comic['name']} is up to date\033[0m")

		sleep(1)

# Verify local files against the database
def check(base_dir, comics, regenerate):
	# Iterate over local files given by the paths in the database
	for path in comics["paths"]:
		for comic in (base_dir / path).iterdir():
			tmp = comic.name.split(" - ")

			# Report new items and add them to the database
			if tmp[1] not in comics["finished"]:
				print(f"{tmp[1]} - found locally but not in the database")
				comics["finished"][tmp[1]] = {"artist": tmp[0], "tags": ""}

	# Write out a new database file if required
	if regenerate:
		new_database = base_dir / "comics_NEW.json"
		print(f"Writing new database file to {new_database}")
		with open(new_database, "w") as f:
			json.dump(comics, f, indent = 4)

if __name__ == "__main__":
	# Read the arguments given to the script
	parser = ArgumentParser(description="Update local comics based on a database file")
	parser.add_argument("-c", "--check", action="store_true", help="verify finished comics folders against the database")
	parser.add_argument("-r", "--regenerate", action="store_true", help="create a new database file based on the existing")
	args = parser.parse_args()

	# Perform setup and either check the database or download updates
	base_dir, comics = setup()
	if args.check or args.regenerate:
		check(base_dir, comics, args.regenerate)
	else:
		download_updates(base_dir, comics["ongoing"])
