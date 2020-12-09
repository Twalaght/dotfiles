# Source the bashrc if running bash
if [ -n "$BASH" ] && [ -r $HOME/.bashrc ]; then
	. $HOME/.bashrc
fi

# Add scripts to path
export PATH="${PATH}:$HOME/.scripts/"

# Export some environmental variables
export MUSIC_PATH="/mnt/f/Media/Music"
