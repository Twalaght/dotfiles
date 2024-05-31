# Disable the system beep
unsetopt BEEP

# Set history options
export HISTFILE="$ZDOTDIR/.zsh_history"
export HISTSIZE=10000
export SAVEHIST=10000
setopt HIST_IGNORE_ALL_DUPS
setopt SHARE_HISTORY
setopt HIST_IGNORE_SPACE

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

# Set the shell prompt
# %F => colour set, %f => colour reset, %~ => pwd, %n => username, %m => host
PROMPT="%F{10}[%n%f%F{12}@%f%F{10}%m%f %F{12}%1~%f%F{10}]%f$ "

# Set the window title, used for WSL
DISABLE_AUTO_TITLE="true"
echo -ne "\033];${PWD##*/}\007"

# Modify the time format for readability
TIMEFMT=$'\nreal\t%*E\nuser\t%*U\nsys\t%*S'

# Load the shell alias file
[[ -f "$HOME/.config/shell/aliasrc" ]] && source "$HOME/.config/shell/aliasrc"

# Load the completion file
[[ -f "$ZDOTDIR/completion.zsh" ]] && source "$ZDOTDIR/completion.zsh"

# Load the autosuggestion file
if [[ -f "$ZDOTDIR/zsh-autosuggestions.zsh" ]]; then
	source "$ZDOTDIR/zsh-autosuggestions.zsh"
	bindkey "^ " autosuggest-accept
	bindkey "^f" forward-word
	ZSH_AUTOSUGGEST_HISTORY_IGNORE="?(#c80,)"
fi
