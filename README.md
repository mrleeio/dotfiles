# dotfiles

Machine-agnostic dotfiles managed with [chezmoi](https://www.chezmoi.io/), supporting three profiles: **personal**, **homelab**, and **work**.

## What's included

| Category | Tools |
|----------|-------|
| Shell | zsh, [zinit](https://github.com/zdharma-continuum/zinit), [starship](https://starship.rs/), [atuin](https://atuin.sh/), [zoxide](https://github.com/ajeetdsouza/zoxide), [fzf](https://github.com/junegunn/fzf) |
| Editor | [neovim](https://neovim.io/) (mini.nvim + LSP), [VS Code](https://code.visualstudio.com/) |
| Terminal | [ghostty](https://ghostty.org/) with Catppuccin theme |
| Git | Commit signing via SSH keys (per-profile) |
| AI | [Claude Code](https://claude.ai/) with custom plugins and MCP servers |
| Versions | [mise](https://mise.jdx.dev/) for runtime management |
| Encryption | [age](https://age-encryption.org/) for sensitive files (SSH config, GitHub hosts) |
| History sync | Self-hosted atuin server on homelab with SQLite |

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

## Machine profiles

All profiles share the same tools and config. Differences:

| | personal | homelab | work |
|---|---|---|---|
| Atuin sync | To homelab (`192.168.1.237`) | Localhost | Disabled |
| Atuin server | No | Yes (LaunchAgent) | No |

Profile data is in `.chezmoidata/machines.yaml`. To change your machine name after init:

```sh
# Edit the cached config
$EDITOR ~/.config/chezmoi/chezmoi.toml
# Change machine_name = "personal" to your profile
```

## Neovim

Uses [mini.nvim](https://github.com/echasnovski/mini.nvim) as the plugin/UI framework with native LSP.

**LSP servers** (installed via Homebrew): gopls, lua_ls, pyright, ruby_lsp, ts_ls

**Key bindings**: `<leader>` is `\`

| Key | Action |
|-----|--------|
| `<leader>f` + `f/g/b/h` | Find files / grep / buffers / help |
| `<leader>e` | File explorer |
| `gd` / `gr` / `gI` | Go to definition / references / implementation |
| `K` | Hover docs |
| `<leader>ca` / `<leader>rn` | Code action / rename |
| `Ctrl-hjkl` | Window navigation |
| `Shift-hl` | Previous/next buffer |

**Tree-sitter** parsers auto-install on startup (requires `tree-sitter-cli`).

## Encryption

Sensitive files are encrypted with age:

- `private_dot_ssh/private_config.tmpl` — SSH config (per-profile host/key mapping)
- `dot_config/gh/encrypted_private_hosts.yml.age` — GitHub CLI hosts

To set up encryption on a new machine, copy your existing key:

```sh
# Copy from another machine (required — a new key can't decrypt existing secrets)
scp other-machine:~/.config/chezmoi/key.txt ~/.config/chezmoi/key.txt

# Then re-apply to decrypt encrypted files
chezmoi apply
```

The public key (recipient) is stored in `.chezmoi.toml.tmpl`. If you need to start fresh with a new key, generate one with `age-keygen -o ~/.config/chezmoi/key.txt`, update the recipient in `.chezmoi.toml.tmpl`, and re-encrypt all files.

## Adding packages

Edit `.chezmoidata/packages.yaml` and add to the appropriate list:

```yaml
packages:
  darwin:
    brews:
      - new-package  # https://example.com/
    casks:
      - new-app      # https://example.com/
```

Packages install automatically on `chezmoi apply` (via `brew bundle`).

## Docs

- [Atuin sync setup](docs/atuin-sync.md) — Self-hosted history sync between machines
- [Git commit signing](docs/git-signing.md) — SSH key signing setup (per-profile)
- [Neovim](docs/neovim.md) — Plugin architecture, key bindings, adding LSP servers

## Structure

```
.chezmoidata/          Data files (machines, packages)
.chezmoiscripts/       Install scripts (darwin, universal)
.chezmoitemplates/     Shared templates (shell-header, claude-settings)
dot_config/            ~/.config/ (nvim, atuin, ghostty, starship, mise, gh)
dot_claude/            Claude Code settings
private_Library/       macOS LaunchAgents, VS Code settings
private_dot_ssh/       SSH config (encrypted)
```
