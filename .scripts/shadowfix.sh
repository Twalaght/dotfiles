#!/bin/bash

# Get number of audio streams from the target
n_audio=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$1" | wc -w)

# Exit out if we had anything other than two audio streams
[[ "$n_audio" == "1" ]] && echo "Nothing to do!" && exit
[[ "$n_audio" != "2" ]] && echo "Did not have two audio streams" && exit

# Rename the input file before converting
new_name="${1%.*}_ORIG.${1##*.}"
mv "$1" "$new_name"

# Export the file with merged audio streams
ffmpeg -hide_banner -loglevel error -i "$new_name" \
	-filter_complex "[0:a:1] pan=mono|c0=FL [l] ; [0:a:0] [l] amix=inputs=2 [a]" \
	-map "0:v:0" -map "[a]" -c:v copy -c:a aac -b:a 192k "$1"
