#!/usr/bin/python3

import argparse
import os
import re
import urllib.request
from pathlib import Path
from requests import get

# Take the reddit video url as an argument
parser = argparse.ArgumentParser(description="Download a video hosted on reddit")
parser.add_argument("url", metavar="url", type=str, help="Reddit URL to download from")
args = parser.parse_args()

# Send a get request and find the video source url
json = get(f"{args.url}.json", headers={"User-Agent": "Wirewolf"}).json()
title = json[0]["data"]["children"][0]["data"]["title"]
json = json[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]

# Create a downloadable link for video and audio
video = re.sub(r"\?.*$", "", json)
audio = re.sub(r"[0-9]+.mp4\?.*$", "audio.mp4", json)

# Sanitize the title to be valid for a file
title = title.replace(" ", "_")
title = re.sub(r"\W+", "", title)

# Download the audio and video
urllib.request.urlretrieve(video, Path.cwd() / "video.mp4")
urllib.request.urlretrieve(audio, Path.cwd() / "audio.mp4")

# Combine the two files in ffmpeg
os.system(f"ffmpeg -i {Path.cwd() / 'video.mp4'} -i {Path.cwd() / 'audio.mp4'} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {title}.mp4 2> /dev/null")

# # Delete the two temp files
os.remove(Path.cwd() / "video.mp4")
os.remove(Path.cwd() / "audio.mp4")
