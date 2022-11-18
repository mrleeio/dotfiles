# dotfiles - Warp Edition

Dotfiles are plain text configuration files on Unix-y systems for things like our shell, ~/.zshrc, our editor in ~/.vimrc, and many others. They are called "dotfiles" as they typically are named with a leading . making them hidden files on your system, although this is not a strict requirement.

Since these files are all plain text, we can gather them together in a git repository and use that to track the changes you make over time.

Many of the dotfiles import `*.local` versions of themselves to encourage customization.

A **opinionated setup** script exists to get yourself work ready without much thought.  Comes with a limited warranty from _Michael Lee_.

## Prerequisites

1. Perform all system updates

2. [Generate an ssh key for github](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/) and [create a personal access token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/).

3. Run the [lendesk laptop setup script](https://github.com/BetterOfficeApps/laptop).

## Requirements

Operating System support:

* macOS BigSur 11.x

Older versions may work but aren't regularly tested.

## Install

These dotfiles are meant to be used and manged with [chezmoi](https://www.chezmoi.io).

Initialize and apply dotfiles with `chezmoi`:

```
chezmoi init --apply git@github.com:mrleeio/dotfiles.git
```

Pull and apply the latest changes from your repo with:

```
chezmoi update
```

### Interesting Commands

See what changes would be applied without applying them:

```
chezmoi diff
```

### Neat Things

Update homebrew and all dependencies, run a health check:

```
brew-up
```

Update or install vim plugins defined in `~/.vimrc.bundles.local`:

```
vim-up
```