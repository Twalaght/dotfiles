#!/bin/sh

# Get the current system volume
volume=$(pacmd dump-volumes | awk 'NR==1{print $8}' | sed 's/\%//')

if [ "$1" = "+" ]; then
	# Unmute if audio is increased, and bound to 100%
	if [ "$volume" -le 98 ]; then
		pactl set-sink-volume 0 +2%
		pactl set-sink-mute 0 no
	fi
elif [ "$1" = "-" ]; then
	# Do not unmute if audio is decreased, and bound to 0%
	if [ "$volume" -gt 2 ]; then
		pactl set-sink-volume 0 -2%
	else
		pactl set-sink-volume 0 0%
		pactl set-sink-mute 0 yes
	fi
elif [ "$1" = "m" ]; then
	pactl set-sink-mute 0 toggle
fi
