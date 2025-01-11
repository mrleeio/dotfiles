# dotfiles

Dotfiles are plain text configuration files on Unix-y systems for things like our shell, ~/.zshrc, our editor in ~/.vimrc, and many others. They are called "dotfiles" as they typically are named with a leading . making them hidden files on your system, although this is not a strict requirement.

Since these files are all plain text, we can gather them together in a git repository and use that to track the changes you make over time.

## Prerequisites

1. Perform all system updates

2. Install homebrew

3. Install chezmoi

4. Install 1Password and enable SSH

## Requirements

Operating System support:

* macOS Sequoia 15.x

Older versions may work but aren't regularly tested.

## Install

These dotfiles are meant to be used and manged with [chezmoi](https://www.chezmoi.io).

Initialize and apply dotfiles with `chezmoi`:

```
chezmoi init --apply https://github.com/mrleeio/dotfiles.git
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