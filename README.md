# dotfiles

A modern, automated macOS dotfiles setup using [chezmoi](https://www.chezmoi.io) with advanced features including encryption, declarative package management, and Claude AI integration.

Dotfiles are plain text configuration files for things like our shell (~/.zshrc), our editor (~/.vimrc), and many others. They are called "dotfiles" as they typically are named with a leading . making them hidden files on your system, although this is not a strict requirement.

Since these files are all plain text, we can gather them together in a git repository and use that to track the changes you make over time.

## Requirements

**macOS only** - This dotfiles setup is designed exclusively for macOS Sequoia 15.x or newer.

Before installing, ensure you have:

1. **System updates** - Run Software Update to ensure macOS is current

2. **[Homebrew](https://brew.sh/)** - Package manager for macOS

3. **Chezmoi** - Install via Homebrew
   ```bash
   brew install chezmoi
   ```

4. **Age encryption key** - Required for decrypting sensitive files
   - If migrating from another machine: Copy your existing `~/.config/chezmoi/key.txt`
   - If setting up fresh: Generate a new key with `age-keygen -o ~/.config/chezmoi/key.txt`
   - Encrypted files: `.ssh/config`, `.config/gh/hosts.yml`

5. **1Password** (recommended) - For SSH and secret management
   - [Download 1Password](https://1password.com/downloads/mac/)
   - Enable SSH agent in 1Password settings

Note: Older macOS versions may work but aren't regularly tested.

## Install

These dotfiles are managed with [chezmoi](https://www.chezmoi.io), a powerful dotfile manager with templating, encryption, and cross-machine support.

**One-command setup** - Initialize and apply dotfiles:

```bash
chezmoi init --apply https://github.com/mrleeio/dotfiles.git
```

This will:
- Clone the dotfiles repository
- Install configured Homebrew packages automatically
- Set up encryption (you'll be prompted for your email)
- Apply all configurations to your home directory
- Install Vim plugins automatically
- Sync Claude Desktop and Code settings

**Keep up to date** - Pull and apply the latest changes:

```bash
chezmoi update
```

## Claude Integration

This repository includes comprehensive Claude AI integration with unified configuration for both Claude Desktop and Claude Code.

### Configuration Files

- **Skills**: `~/.claude/skills/` (custom Claude Code skills)

### Claude Code Skills

Custom skills enhance Claude Code's capabilities. This repository includes two skills in `~/.claude/skills/`:

**conventional-commits** - Formats git commits following Conventional Commits standard:
- Uses conventional commit types (feat, fix, docs, refactor, etc.)
- No AI attribution in commits
- Clean, professional commit history

**Creating your own skills**: See [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)

## Starship Prompt

This dotfiles setup uses [Starship](https://starship.rs), a fast, customizable, and minimal shell prompt written in Rust. Starship provides a modern, informative command-line experience with intelligent context awareness.

### What is Starship?

Starship is a cross-shell prompt that shows relevant information based on your current directory and context:
- **Git status** - Branch, changes, stash count
- **Language versions** - Node, Python, Ruby, Go, Rust, etc.
- **Package versions** - From package.json, Cargo.toml, etc.
- **Execution time** - For long-running commands
- **Exit codes** - Visual indication of command success/failure
- **And much more** - Docker context, AWS profile, Kubernetes, etc.

### Installation

Starship is automatically installed via Homebrew as part of this dotfiles setup (defined in `.chezmoidata/packages.yaml`).

### Configuration

Starship can be customized via `~/.config/starship.toml`.

See the [Starship Configuration Documentation](https://starship.rs/config/) for all available options.

## Key Configuration Files

### Declarative Packages (`.chezmoidata/packages.yaml`)
All Homebrew packages are defined here and automatically installed via run scripts:
- **Brews**: CLI tools
- **Casks**: GUI applications

### Git Configuration (`dot_gitconfig.tmpl`)
Templated git config with:
- User email from chezmoi data
- Modern git aliases and settings
- Commit message templates

### Vim Configuration

Vim is configured with a modern plugin setup using [vim-plug](https://github.com/junegunn/vim-plug):

**Configuration files**:
- `~/.vimrc` - Main Vim configuration
- `~/.vimrc.bundles` - Plugin definitions
- `~/.vim/autoload/plug.vim` - vim-plug plugin manager

**Included plugins**:
- **fzf** - Fuzzy finder integration
- **NERDTree** - File explorer
- **vim-fugitive** - Git integration
- **ALE** - Asynchronous linting (if Vim 8.0+)
- **vim-test** - Test runner integration
- And more (see `~/.vimrc.bundles`)

**Automatic setup**: Vim plugins are automatically installed on first `chezmoi apply` via a run script.

**Manual management**:
- Update plugins: `vim-up`
- Install new plugins: Add to `~/.vimrc.bundles`, then run `vim-up`
- Remove plugins: Delete from `~/.vimrc.bundles`, then run `vim-up`

## Useful Commands

### Chezmoi Operations

See what changes would be applied without applying them:
```bash
chezmoi diff
```

Apply all dotfile changes:
```bash
chezmoi apply
```

Update from git repository:
```bash
chezmoi update
```

Edit a managed file:
```bash
chezmoi edit ~/.zshrc
```

Add a new file to be managed:
```bash
chezmoi add ~/.config/newfile
```

### Custom Scripts

Update homebrew and all dependencies, run a health check:
```bash
brew-up
```

Update or install Vim plugins (automatically installed on first setup):
```bash
vim-up
```

Enhanced git pull with upstream tracking:
```bash
git-up
```

Kill a process on a specific port:
```bash
clear-port 3000
```

### Automatic Daily Updates

Your shell automatically runs `brew-up` and `vim-up` once per day on the first shell startup. The timestamp is tracked in `~/.cache/last-daily-update`. This keeps your packages and Vim plugins up to date without manual intervention.

To manually trigger updates:
```bash
brew-up  # Update Homebrew packages
vim-up   # Update Vim plugins
```

To disable automatic updates, remove the `daily-update` call from `~/.zshrc`.

## Package Management

This repository uses declarative package management for macOS via Homebrew. To add a new package:

1. Edit `.chezmoidata/packages.yaml`:
   ```yaml
   packages:
     darwin:
       brews:
         - package-name  # https://package-url
       casks:
         - app-name      # https://app-url
   ```

2. Apply with chezmoi:
   ```bash
   chezmoi apply
   ```

The package will be automatically installed via Homebrew on the next apply.

## Advanced Features

### Encryption

Sensitive files are encrypted using Age:
- Files in `private_*` directories are automatically encrypted
- Secrets can be templated using chezmoi's data variables
- Configure encryption in `.chezmoi.toml.tmpl`

### Run Scripts

Scripts in `.chezmoiscripts/` run automatically:
- `run_onchange_*` - Run when file changes
- `run_once_*` - Run only once
- Used for package installation and system setup

## Troubleshooting

### Chezmoi Issues

**Problem**: Changes not applying
```bash
# Force re-application
chezmoi apply --force

# Check for errors
chezmoi apply --verbose
```

**Problem**: Encryption not working
```bash
# Verify Age setup
age --version

# Check chezmoi config
chezmoi doctor
```

### Package Installation Issues

**Problem**: Homebrew packages not installing
```bash
# Check run scripts
ls -la ~/.local/share/chezmoi/.chezmoiscripts/
```

**Problem**: Missing dependencies
```bash
# Update Homebrew
brew update

# Check for issues
brew doctor
```

## License

This repository is available for personal use and customization. Feel free to fork and adapt to your needs.