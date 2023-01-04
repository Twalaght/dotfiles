# Disable the system beep
unsetopt BEEP

# Set history options
export HISTFILE="$ZDOTDIR/.zsh_history"
export HISTSIZE=10000
export SAVEHIST=10000
setopt HIST_IGNORE_ALL_DUPS
setopt SHARE_HISTORY

# Set up directory stack
setopt AUTO_PUSHD           # Push the current directory visited on the stack
setopt PUSHD_IGNORE_DUPS    # Do not store duplicates in the stack
setopt PUSHD_SILENT         # Do not print the directory stack after pushd or popd

# Alias "d" to show directory history, then 1-9 to jump to a specific directory
alias d="dirs -v"
for index ({1..9}) alias "$index"="cd +${index}"; unset index

# Enable vi mode and history searching
bindkey -v
export KEYTIMEOUT=1
bindkey -v "^?" backward-delete-char
bindkey "^R" history-incremental-search-backward

# Pressing "v" in vi normal mode edits the command in editor
autoload -Uz edit-command-line
zle -N edit-command-line
bindkey -M vicmd v edit-command-line

# Support vi mode opearting on text objects
autoload -Uz select-bracketed select-quoted
zle -N select-quoted
zle -N select-bracketed
for km in viopp visual; do
	bindkey -M $km -- '-' vi-up-line-or-history
	for c in {a,i}${(s..)^:-\'\"\`\|,./:;=+@}; do
		bindkey -M $km $c select-quoted
	done
	for c in {a,i}${(s..)^:-'()[]{}<>bB'}; do
		bindkey -M $km $c select-bracketed
	done
done

# Mimic the behaviour of vim surround in vi mode
autoload -Uz surround
zle -N delete-surround surround
zle -N add-surround surround
zle -N change-surround surround
bindkey -M vicmd cs change-surround
bindkey -M vicmd ds delete-surround
bindkey -M vicmd ys add-surround
bindkey -M visual S add-surround

# Set the shell prompt
# %F => colour set, %f => colour reset, %~ => pwd, %n => username, %m => host
PROMPT="%F{10}[%n%f%F{12}@%f%F{10}%m%f %F{12}%1~%f%F{10}]%f$ "

# Set the window title, used for WSL
DISABLE_AUTO_TITLE="true"
echo -ne "\033];${PWD##*/}\007"

# Enable git status on the right side prompt
autoload -Uz vcs_info
setopt PROMPT_SUBST
precmd_functions+=(vcs_info)
RPROMPT='${vcs_info_msg_0_}'

# Modify the time format for readability
TIMEFMT=$'\nreal\t%*E\nuser\t%*U\nsys\t%*S'

# Enable checking for changes to the repo, and custom strings for each
zstyle ":vcs_info:*" check-for-changes true
zstyle ":vcs_info:*" unstagedstr "*"   # Unstaged changes
zstyle ":vcs_info:*" stagedstr   "+"   # Staged changes
# Set the format of the git information
# %b => branch name, %u => unstaged, %c => staged, %a => current git action
zstyle ":vcs_info:git:*" formats       "%F{10}[%f%F{12}%b%u%c%f%F{10}]%f"
zstyle ":vcs_info:git:*" actionformats "%F{10}[%f%F{12}b|%a%u%c%f%F{10}]%f"

# Load the shell alias file
[[ -f "$HOME/.config/shell/aliasrc" ]] && source "$HOME/.config/shell/aliasrc"
# Load the shell function file
[[ -f "$HOME/.config/shell/funcrc" ]] && source "$HOME/.config/shell/funcrc"
# Load the completion file
[[ -f "$ZDOTDIR/completion.zsh" ]] && source "$ZDOTDIR/completion.zsh"

