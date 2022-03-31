#!/bin/sh

# Convert comic folders to a zipped tachi format
for arg in "$@"; do
	# Remove folder if it exists, then create it
	[ -d /tmp/comics/"$arg" ] && rm -rf /tmp/comics/"$arg"
	mkdir -p /tmp/comics/"$arg"

	# Check if the comic has one chapter, or multiple
	if [ -z "$(find "$arg" -mindepth 1 -type d)" ]; then
		# Zip the images in the specified comic
		zip -rjq /tmp/comics/"$arg"/ch1.zip "$arg"

		# Copy the cover image
		cover=$(find "$arg" | head -2 | tail -1)
		cp "$cover" /tmp/comics/"$arg"/cover."${cover##*.}"
	else
		# Zip the images for each chapter in the comic
		i=1
		for d in "$arg"*/; do
			zip -rjq /tmp/comics/"$arg"/ch"$i".zip "$d"
			i=$((i+1))
		done

		# Copy the cover image
		cover=$(find "$arg" | head -3 | tail -1)
		cp "$cover" /tmp/comics/"$arg"/cover."${cover##*.}"
	fi
done

# Open the processed folder in explorer if possible
[ -x "$(command -v explorer.exe)" ] && cd /tmp/comics/ && explorer.exe .
