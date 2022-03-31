#!/usr/bin/python3

import argparse
from os import remove
from pathlib import Path
from re import sub
from requests import get
from shutil import copyfile
from subprocess import call
from urllib.request import urlretrieve

# Take the reddit video url as an argument
parser = argparse.ArgumentParser(description="Download a video hosted on reddit")
parser.add_argument("url", metavar="url", type=str, help="Reddit URL to download from")
args = parser.parse_args()

# Set the header and send a get request and find the video source url
headers = {"User-Agent": "Redsave"}
json = get(f"{args.url}.json", headers = headers).json()
url = json[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]

# Create a downloadable link for video and audio
video = sub(r"\?.*$", "", url)
audio = sub(r"[0-9]+.mp4\?.*$", "audio.mp4", url)

# Set the title of the video and limit the length
title = json[0]["data"]["children"][0]["data"]["title"].replace(" ", "_")
title = sub(r"\W+", "", title)
title = f"{title[:100]}.mp4"

# Check if the target video has audio
has_audio = get(audio, headers = headers).status_code == 200

# Download the video component
urlretrieve(video, Path("/tmp/video.mp4"))

# Check if the target has audio
if get(audio, headers = headers).status_code == 200:
	# If the file has audio, download it and merge with ffmpeg
	urlretrieve(audio, Path("/tmp/audio.mp4"))
	command = f"ffmpeg -i {Path('/tmp/video.mp4')} -i {Path('/tmp/audio.mp4')} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {Path.cwd() / title} > /dev/null 2>&1"
	call(command, shell = True)

else:
	# If no audio is present, just copy the video
	copyfile(Path("/tmp/video.mp4"), Path.cwd() / title)

# Remove the temporary files
remove(Path("/tmp/video.mp4"))
if has_audio: remove(Path("/tmp/audio.mp4"))
