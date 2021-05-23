# ensure dotfiles bin directory is loaded first
PATH="$HOME/.bin:/usr/local/sbin:$PATH"

# sublime text
PATH="/Applications/Sublime Text.app/Contents/SharedSupport/bin:$PATH"

# chruby
source /usr/local/opt/chruby/share/chruby/chruby.sh
source /usr/local/opt/chruby/share/chruby/auto.sh

# fnm
eval "$(fnm env)"

# direnv
eval "$(direnv hook zsh)"

# gpg
export GPG_TTY=$(tty)

# mkdir .git/safe in the root of repositories you trust
PATH=".git/safe/../../bin:$PATH"

export -U PATH
