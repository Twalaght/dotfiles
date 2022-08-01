#!/usr/bin/python3

from bs4 import BeautifulSoup
from e6pd import gen_headers, e6pd, parallel_download
from multiprocessing import Pool, cpu_count
from os import getenv
from pathlib import Path
from requests import get
from sqlite3 import connect
from time import sleep

# Read in a watchlist from a database
def read_db(watchlist, table):
	# Ensure the watchlist database exists
	if not watchlist.exists():
		print(f"Error - watchlist.db does not exist at {watchlist_path}")
		exit(1)

	# Connect to the database and execute a query
	query = f"SELECT * FROM {table}"
	cursor = connect(watchlist).cursor()
	cursor.execute(query)

	# Fetch and output result
	result = cursor.fetchall()
	cursor.close()
	return result

# Update a database entry with the newest page link
def update_page(watchlist, page, name):
	# Connect to the database and execute a query
	query = f"UPDATE webcomics SET url = '{page}' WHERE name = '{name}'"
	db = connect(watchlist)
	cursor = db.cursor()
	cursor.execute(query)

	# Commit to the database and close the connection
	db.commit()
	cursor.close()

# Collect images from starting point of a webcomic
def chain(base_dir, comic):
	# Count the number of files present locally
	local_num = 1
	for page in Path(base_dir / comic[2]).iterdir():
		if page.is_file(): local_num += 1

	# Iterate through pages to collect the links to new images
	page = comic[0]
	images = []
	while True:
		# Extract the image URL and print a status message
		soup = BeautifulSoup(get(page).text, "html.parser")
		images.append(parser[comic[3]].image(soup))
		print(f"[Collected {len(images)} pages]", end = "\r")

		# If the final page is reached, break out of the loop
		old_page = page
		page = parser[comic[3]].page(soup)
		if not page or page == old_page:
			page = old_page
			print()
			break

	# Prevent downloading the most recent page twice
	if local_num != 1: images = images[1:]

	# Generate download arguments from the fetched images
	args = []
	for i in range(len(images)):
		ext = images[i].split(".")[-1]
		name = f"{comic[1]} {local_num + i:04}.{ext}"
		path = base_dir / comic[2] / name
		args.append((images[i], path, i + 1, len(images)))

	return page, args

# Define image and page behavior for each webcomic
class pix_and_hen:
	def image(soup):
		image = soup.find("div", {"class": "col-lg-8 container-fluid text-center"})
		return image.figure.img["src"].split("?")[0]
	def page(soup):
		next_page = soup.find("a", {"rel": "next"})
		return next_page["href"] if next_page else None
class housepets:
	def image(soup):
		image = soup.find("div", {"id": "comic"})
		return image.find("img")["src"]
	def page(soup):
		next_page = soup.find("a", {"class": "navi comic-nav-next navi-next"})
		return next_page["href"] if next_page else None

parser = {"pix_and_hen": pix_and_hen, "housepets": housepets}

# Set the base directory from the environment variable
base_dir = getenv("COMIC_PATH")
if base_dir is None:
	print(f"Error - COMIC_PATH environment variable is not set")
	exit(1)

# Set the base comic directory, generate headers, and read the database
base_dir = Path(base_dir)
headers = gen_headers()
e6_comics = read_db(base_dir / "watchlist.db", "e621_comics")
web_comics = read_db(base_dir / "watchlist.db", "webcomics")

# Sort the fetched comics entries by name
e6_comics.sort(key = lambda x: x[1])
web_comics.sort(key = lambda x: x[1])

# Process each comic hosted on e621
for comic in e6_comics:
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

# Process each webcomic
for comic in web_comics:
	# Ensure the target comic folder exists
	if not Path(base_dir / comic[2]).exists():
		print(f"WARNING - Folder {comic[2]} does not exist")
		continue

	# Get the link to the next page
	soup = BeautifulSoup(get(comic[0]).text, "html.parser")
	page = parser[comic[3]].page(soup)

	# Continue if the latest page has not changed
	if not page or page == comic[0]:
		print(f"\033[32m{comic[1]} is up to date\033[0m")
		continue

	# Print a status message and collect the new pages
	print(f"* {comic[1]} has new pages")
	new_page, args = chain(base_dir, comic)

	# Create a pool of threads, and use them to download in parallel
	Pool(cpu_count()).starmap(parallel_download, args, chunksize = 1)

	# Update the database entry and print a closing status message
	update_page(base_dir / "watchlist.db", new_page, comic[1])
	print(f"\n[Finished {comic[1]}]")
