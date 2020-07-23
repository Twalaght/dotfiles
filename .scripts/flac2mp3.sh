#!/bin/bash

# Determine which files are present in FLAC folder, but not in MP3 folder
# Ignores album art, and sanitizes output to be only file names
flac_list=$(find "$MUSIC_PATH"/FLAC -type f -printf "%f\n" | sed -e '/^AlbumArt/d' -e 's/\.[^.]*$//')
mp3_list=$(find "$MUSIC_PATH"/MP3 -type f -printf "%f\n" | sed -e '/^AlbumArt/d' -e 's/\.[^.]*$//')

# Take the difference of each file list
diff_out=$(diff <(echo "$flac_list") <(echo "$mp3_list") | grep "<" | sed 's/< //')

# If no changes need to be made, exit the script
if [ -z "$diff_out" ]; then
	echo -e "\e[32mNothing to do!\e[39m"
	exit 0
fi

# Create MP3 copies of any files that do not already have one
while IFS= read -r title; do
	# Store the input and output paths for the given song 
	flac_path="$MUSIC_PATH/FLAC/$title.flac"
	mp3_path="$MUSIC_PATH/MP3/$title.mp3"

	# Print a status message
	printf "%s" "Converting $title... "

	# Convert each FLAC song to an MP3 copy
	if ffmpeg -i "$flac_path" -ab 320k -map_metadata 0 -id3v2_version 3 -nostdin -loglevel 0 "$mp3_path"; then 
		# Print a green "done" on success
		echo -e "\e[32mdone\e[39m"
	else
		# Print a red "ERROR" on failure
		echo -e "\e[31mERROR\e[39m"
	fi
done <<< "$diff_out"
