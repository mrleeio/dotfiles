# Custom functions

# No arguments: `git status`
# With arguments: acts like `git`

function g() {
  if [[ $# -gt 0 ]]; then
    git "$@"
  else
    git status
  fi
}

# Fast Node Manager
#
# https://github.com/Schniz/fnm

eval "$(fnm env)"

# Configure Go path

export PATH=$PATH:$(go env GOPATH)/bin

# Custom aliases

alias dev="cd $HOME/GitHub"
alias mdev="cd $HOME/GitHub/mrleeio"

alias vimup="vim -u $HOME/.vimrc.bundles +PlugUpdate +PlugClean! +qa"

alias ch="chezmoi"

alias be="bundle exec"
alias ber="bundle exec rubocop"
