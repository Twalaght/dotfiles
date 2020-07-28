#!/bin/sh

# Sync music folders to phone over ssh
rsync -av --ignore-existing -e "ssh -p 2222" "$MUSIC_PATH/FLAC/" twi@"$PHONE_IP":SDCard/Music/FLAC
