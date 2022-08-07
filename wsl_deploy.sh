#!/bin/sh

mkdir -p "$HOME"/.config
cp -r .config/nvim "$HOME"/.config/nvim
cp -r .config/shell "$HOME"/.config/shell
cp -r .scripts "$HOME"/scripts
cp .bashrc "$HOME"
cp .profile "$HOME"
sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim \
	--create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
