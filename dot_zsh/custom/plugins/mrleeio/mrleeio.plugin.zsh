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

# Custom aliases

alias dev="cd $HOME/GitHub"
alias mdev="cd $HOME/GitHub/mrleeio"
alias vdev="cd $HOME/GitHub/verygoodsecurity"

alias vimup="vim -u $HOME/.vimrc.bundles +PlugUpdate +PlugClean! +qa"

alias ch="chezmoi"
alias cha="chezmoi init --apply git@github.com:mrleeio/dotfiles.git"

alias thi="pip3 install things-cli"
alias th="things-cli"
alias thva="things-cli -a 5DmEHnWdVDnAbGKRzNpuGd --recursive anytime"
alias tht="things-cli today"

alias be="bundle exec"
alias ber="bundle exec rubocop"
