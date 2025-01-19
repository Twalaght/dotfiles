# Bootstrap zinit, downloading it if required
ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"
if [ ! -d "$ZINIT_HOME" ]; then
	mkdir -p "$(dirname $ZINIT_HOME)"
	git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi
source "${ZINIT_HOME}/zinit.zsh"

# Load zsh plugins
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions

# Autosuggest customisation
bindkey "^ " autosuggest-accept
bindkey "^f" forward-word
ZSH_AUTOSUGGEST_HISTORY_IGNORE="?(#c80,)"

# Load completions
autoload -Uz compinit && compinit

# Initialise homebrew if present
if [ -f "/opt/homebrew/bin/brew" ]; then
	eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Disable the system beep
unsetopt BEEP

# Prevent python from writing excess bytecode
export PYTHONDONTWRITEBYTECODE=1

# Set history options
HISTFILE="$ZDOTDIR/.zsh_history"
HISTSIZE=10000
SAVEHIST=10000
setopt appendhistory
setopt sharehistory
setopt hist_ignore_space
setopt hist_ignore_all_dups
setopt hist_save_no_dups
setopt hist_ignore_dups

# Alias "d" to show directory history, then 1-9 to jump to a specific directory
setopt AUTO_PUSHD         # Push the current directory visited on the stack
setopt PUSHD_IGNORE_DUPS  # Do not store duplicates in the stack
setopt PUSHD_SILENT       # Do not print the directory stack after pushd or popd
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

