# ensure dotfiles bin directory is loaded first
PATH="$HOME/.bin:/usr/local/sbin:$PATH"

# mkdir .git/safe in the root of repositories you trust
PATH=".git/safe/../../bin:$PATH"

# Chruby - https://github.com/postmodern/chruby
source $HOMEBREW_PREFIX/opt/chruby/share/chruby/chruby.sh
source $HOMEBREW_PREFIX/opt/chruby/share/chruby/auto.sh

# fnm - https://github.com/Schniz/fnm
eval "$(fnm env --use-on-cd)"

export -U PATH