# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Disable the system bell
bind "set bell-style none"

# Misc shell options
export HISTFILE="$HOME/.config/shell/bash/bash_history"
HISTCONTROL=ignoreboth
HISTSIZE=10000
HISTFILESIZE=10000
shopt -s histappend
shopt -s checkwinsize
set -o vi
bind -m vi-command "Control-l: clear-screen"
bind -m vi-insert "Control-l: clear-screen"

# Set the PS1 prompt with terminal colours
GREEN="\e[38;5;10m"
BLUE="\e[38;5;12m"
CLEAR="\e[m"
PS1="${GREEN}[\u${BLUE}@${GREEN}\h ${BLUE}\W${GREEN}]${CLEAR}$ "

# If the alias file is present, load it
[[ -f "$HOME/.config/shell/aliasrc" ]] && source "$HOME/.config/shell/aliasrc"

# Default tmux instance
tm() {
	name="main"
	if tmux ls &> /dev/null; then
		tmux attach
	else
		tmux new -s "$name" -d
		tmux split-window -h -p 25
		tmux last-pane

		if ! [ -z "$1" ]; then
			pane="$name:0.0"
			tmux send-keys -t "$pane" "$EDITOR $1" Enter
		fi

		tmux attach-session -t "$name"
	fi
}
