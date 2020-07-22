#!/bin/sh

# Clone the dotfiles repo containing the scripts
git -C /tmp clone --quiet https://github.com/Twalaght/dotfiles

# Copy the scripts folder to home
cp -r /tmp/dotfiles/.scripts ~

# Remove the temp repo
rm -rf /tmp/dotfiles
