# Bash shell configuration

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Misc shell options
export HISTFILE=$HOME/.config/shell/bash_history
HISTCONTROL=ignoreboth
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s histappend
shopt -s checkwinsize
set -o vi

# Set the default editors to nvim
export EDITOR="nvim"
export VISUAL="nvim"

# Shortcuts to edit and source this file
alias ec="$EDITOR $HOME/.bashrc"
alias sc="source $HOME/.bashrc"

# If the alias file is present, load it
[[ -f $HOME/.config/shell/aliasrc ]] && source $HOME/.config/shell/aliasrc

# Sets the PS1 prompt with terminal colours
PS1="\[\e[38;5;10m\][\u@\h \[\e[38;5;12m\]\W\[\e[38;5;10m\]]\[\e[38;5;15m\]\$ "

# Turn off system bell
bind "set bell-style none"

# Enable persistence for wal colour schemes
[[ -f $HOME/.cache/wal/sequences ]] && (cat ~/.cache/wal/sequences &)
