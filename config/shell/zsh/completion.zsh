# Load complist before compinit
zmodload zsh/complist

# Use vi keys in menu completion
bindkey -M menuselect "h" vi-backward-char
bindkey -M menuselect "k" vi-up-line-or-history
bindkey -M menuselect "j" vi-down-line-or-history
bindkey -M menuselect "l" vi-forward-char

# Add binds to clear and undo
bindkey -M menuselect "^xg" clear-screen
bindkey -M menuselect "^xu" undo

autoload -Uz compinit; compinit
setopt GLOB_COMPLETE     # Show autocompletion menu with globs
setopt GLOBDOTS          # Recognise dot files
setopt AUTO_LIST         # Automatically list choices on ambiguous completion.
setopt COMPLETE_IN_WORD  # Complete from both ends of a word.

# zstyle pattern => :completion:<function>:<completer>:<command>:<argument>:<tag>
# Define completers
zstyle ":completion:*" completer _extensions _complete _approximate

# Enable the completion cache
zstyle ":completion:*" use-cache on
zstyle ":completion:*" cache-path "$ZDOTDIR/.zcompcache"

# Complete the alias when _expand_alias is used as a function
zstyle ":completion:*" complete true
zle -C alias-expension complete-word _generic
bindkey "^Xa" alias-expension
zstyle ":completion:alias-expension:*" completer _expand_alias

# Enable menu selection
zstyle ":completion:*" menu select

# Autocomplete options for cd instead of directory stack
zstyle ":completion:*" complete-options true

# Colour output depending on context of completion
zstyle ":completion:*:*:*:*:corrections" format "%F{yellow}!- %d (errors: %e) -!%f"
zstyle ":completion:*:*:*:*:descriptions" format "%F{blue}-- %D %d --%f"
zstyle ":completion:*:*:*:*:messages" format "%F{purple} -- %d --%f"
zstyle ":completion:*:*:*:*:warnings" format "%F{red} -- no matches found --%f"
zstyle ":completion:*:*:*:*:default" list-colors ${(s.:.)LS_COLORS}

# Only display some tags for "cd"
zstyle ":completion:*:*:cd:*" tag-order local-directories directory-stack path-directories

# Required for completion to be in better groups
zstyle ":completion:*" group-name ""
zstyle ":completion:*:*:-command-:*:*" group-order aliases builtins functions commands

# See ZSHCOMPWID "completion matching control"
zstyle ":completion:*" matcher-list "" "m:{a-zA-Z}={A-Za-z}" "r:|[._-]=* r:|=*" "l:|=* r:|=*"
zstyle ":completion:*" keep-prefix true
zstyle -e ':completion:*:(ssh|scp|sftp|rsh|rsync):hosts' hosts 'reply=(${=${${(f)"$(cat {/etc/ssh_,~/.ssh/known_}hosts(|2)(N) /dev/null)"}%%[# ]*}//,/ })'
