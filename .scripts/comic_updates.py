#!/usr/bin/python3

from e6pd import gen_headers, e6pd
from os import getenv
from pathlib import Path
from requests import get
from sqlite3 import connect
from time import sleep

# Read in a watchlist from a database
def read_db(watchlist_path):
	# Ensure the watchlist database exists
	wl = Path(watchlist_path) / "watchlist.db"
	if not wl.exists():
		print(f"Error - watchlist.db does not exist at {watchlist_path}")
		exit(1)

	# Connect to the database and create a cursor
	db = connect(wl)
	cursor = db.cursor()

	# Write a query and execute it with cursor
	query = "SELECT * FROM e621_comics"
	cursor.execute(query)

	# Fetch and output result
	result = cursor.fetchall()
	cursor.close()
	return result

# Set the base directory from the environment variable
base_dir = getenv("COMIC_PATH")
if base_dir is None:
	print(f"Error - COMIC_PATH environment variable is not set")
	exit(1)

# Set the base comic directory, generate headers, and read the database
base_dir = Path(base_dir)
headers = gen_headers()
comics = read_db(base_dir)

# For each comic in the watchlist check its local data against the server
for comic in comics:
	# Count how many local files we have, with an offset included
	local_num = -comic[3]

	# Ensure the target comic folder exists
	if not Path(base_dir / comic[2]).exists():
		print(f"WARNING - Folder {comic[2]} does not exist")
		continue

	# Count the number of files present locally
	for page in Path(base_dir / comic[2]).iterdir():
		if page.is_file(): local_num += 1

	# Query e621 to find how many pages are listed
	server_num = get(f"https://e621.net/pools/{comic[0]}.json", headers = headers).json()["post_count"]

	# Output a status message depending on the status of the comic
	if local_num < server_num:
		print(f"* {comic[1]} has {server_num - local_num} new pages")

		# If the update flag is set, update the comic
		if comic[4] == 1:
			# Set the offsets corresponding to deleted posts or combined pools
			n_offset = comic[3] if comic[3] > 0 else None
			if comic[3] < 0: local_num += comic[3]

			# Set the download folder and update the required pages
			dl_folder = base_dir / comic[2]
			e6pd(comic[0], comic[1], local_num, n_offset, None, dl_folder, True, headers)

	elif local_num > server_num:
		print(f"\033[34m{comic[1]} is ahead of e6 by {local_num - server_num} pages\033[0m")
	else:
		print(f"\033[32m{comic[1]} is up to date\033[0m")

	sleep(1)



# # Connect to DB and create a cursor
# db = sqlite3.connect("watchlist.db")
# cursor = db.cursor()

# for comic in json_watchlist["comics"]:
# 	id, folder, name, offset = comic.values()
# 	name = name.replace("'","''");
# 	folder = folder.replace("'","''");
# 	query = f"INSERT INTO e621_comics VALUES ({id}, '{name}', '{folder}', {offset})"
# 	cursor.execute(query)

# # Close the cursor and commit
# cursor.close()
# db.commit()
# exit()
