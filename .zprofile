# Shell config
export ZDOTDIR="$HOME/.config/shell/zsh"

# Set nvim as the system default editors
export EDITOR="nvim"
export VISUAL="nvim"

# Disable the bell in less
export LESS="$LESS -R -Q"

# Add scripts to path
export PATH="${PATH}:$HOME/.scripts"
if [[ "$OSTYPE" == "linux-gnu" ]]; then
	export PATH="${PATH}:$HOME/.local/bin"
fi

# Set paths for specific folders
export MUSIC_PATH=""
export COMIC_PATH=""
export AUTH_PATH=""
