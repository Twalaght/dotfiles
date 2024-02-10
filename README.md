# dotfiles
### _Everything you need, nothing you don't_

## Installation
```shell
# Install stow with package manager of choice
sudo apt install stow

# Clone dotfiles repository locally
git@github.com:Twalaght/dotfiles.git ~/dotfiles

# Install with stow
cd dotfiles

stow .  # If home directory is clean

# Otherwise if some dotfiles are already present, use --adopt
stow --adopt .
```
