# ~/.bashrc

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Bash shell options
HISTCONTROL=ignoreboth
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s histappend
shopt -s checkwinsize

# Set the desired PS1, the coloured version uses terminal colours
PS1="\[\e[38;5;10m\][\u@\h \[\e[38;5;12m\]\W\[\e[38;5;10m\]]\[\e[38;5;15m\]\$ "	# Coloured
# PS1="[\u@\h \W]\$ "								# Uncoloured

# Some aliases for convenience
alias ls="ls --color=auto"		# Coloured output
alias grep="grep --color=auto"	# Coloured output
alias ll="ls -hl"				# Human readable sizes, in a list
alias la="ls -hA"				# Human readable sizes, show hidden
alias lal="ls -hlA"				# Human readable sizes, in a list, show hidden
alias cp="cp -i"				# Confirm before overwriting
alias mv="mv -i"				# Confirm before overwriting
alias df="df -h"				# Readable sizes

alias p="sudo pacman"
alias v="nvim"
alias sv="sudo nvim"
alias r="ranger"
alias sr="sudo ranger"
alias ka="killall"
alias g="git"

# Binds
bind "set bell-style none"

# Enable persistence for wal colour schemes
if [[ -f $HOME/.cache/wal/sequences ]]; then
	(cat ~/.cache/wal/sequences &)
fi
