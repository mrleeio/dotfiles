setopt hist_ignore_all_dups inc_append_history
HISTFILE=~/.zhistory
HISTSIZE=50000
SAVEHIST=50000

export ERL_AFLAGS="-kernel shell_history enabled"