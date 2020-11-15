#!/bin/sh

res=$(printf "Lock\nLogout\nSleep\nRestart\nShutdown" | rofi -dmenu -show run -lines 5 -width 10 -p ":>>System<<")

case "$res" in
	Lock) i3lock -c 222222;;
	Sleep) systemctl suspend;;
	Logout) i3-msg exit;;
	Restart) "$HOME"/.scripts/goodnight.sh -r;;
	Shutdown) "$HOME"/.scripts/goodnight.sh;;
esac
