#!/bin/bash

# Set the database path
db="$COMIC_PATH/watchlist.db"

# Get the title only from the folder and remove slashes
title="${1#*- }"
title="${title/\//}"

get_json() {
	# Ensure info exists in database
	result=$(sqlite3 "$db" "SELECT title FROM archive WHERE title LIKE '%$title%'")
	[[ $result ]] || return

	# Build the entry into a json string
	json="{\n"
	for col in title artist tags status; do
		# Get the entry from the database
		query="SELECT $col FROM archive WHERE title LIKE '%$title%'"
		result=$(sqlite3 "$db" "$query")

		# If we have the tags entry, change the name
		if [[ $col == "tags" ]]; then col="genre"; fi

		# Add the entry to the json string
		if [[ $col != "status" ]]; then
			json="$json  \"$col\": \"$result\",\n"
		else
			case $result in
				"Unknown") result=0;;
				"Ongoing") result=1;;
				"Completed") result=2;;
			esac
			json="$json  \"$col\": $result\n}"
		fi
	done

	# Write out the json to a file given as an argument
	echo -e "$json" > "$1"
}

# Remove folder if it exists, then create it
[ -d "/tmp/comics/$1" ] && rm -rf "/tmp/comics/$1"
mkdir -p "/tmp/comics/$1"

# Check if the comic has one chapter, or multiple
if [ -z "$(find "$1" -mindepth 1 -type d)" ]; then
	# Zip the images in the specified comic
	zip -rjq "/tmp/comics/$1/ch1.zip" "$1"

	# Copy the cover image
	cover=$(find "$1" | head -2 | tail -1)
	cp "$cover" /tmp/comics/"$1"/cover."${cover##*.}"
else
	# Zip the images for each chapter in the comic
	i=1
	for d in "$1"/*; do
		zip -rjq "/tmp/comics/$1/ch$i.zip" "$d"
		i=$((i+1))
	done

	# Copy the cover image
	cover=$(find "$1" | head -3 | tail -1)
	cp "$cover" "/tmp/comics/$1/cover.${cover##*.}"
fi

# Get details in a json file if present in the database
get_json "/tmp/comics/$1/details.json"

# Required to allow adb to access the temp files
cd "/tmp/comics/$1" || echo "Couldn't create folder"; exit

# Get SD card name, and push the files to device
sd_card=$(adb shell sm list-volumes public | awk '{print $NF}' | tr -d "\r")
adb push "/tmp/comics/$1" "/storage/$sd_card/Tachiyomi/local"

# Remove the temp files
rm -r "/tmp/comics"
