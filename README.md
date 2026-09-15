# dotfiles

Machine-agnostic dotfiles managed with [chezmoi](https://www.chezmoi.io/), supporting three profiles: **personal**, **homelab**, and **work**.

## What's included

| Category | Tools |
|----------|-------|
| Shell | zsh, [starship](https://starship.rs/), [atuin](https://atuin.sh/), [zoxide](https://github.com/ajeetdsouza/zoxide) |
| Editor | [Neovim](https://neovim.io/) configuration (mini.nvim + LSP) |
| Terminal | [ghostty](https://ghostty.org/) with Catppuccin theme |
| Git | Profile-specific identity, SSH authentication, and commit signing through 1Password |
| AI | Claude Code and Codex with shared instructions, sandbox policies, and Conventional Commits |
| Versions | [mise](https://mise.jdx.dev/) for runtime management |
| History | Local-only Atuin history; automatic sync and update checks disabled |

This repository applies configuration only. It does not install software, change
login shells, load credentials, or start background services.

## Quick Start

For macOS Sequoia 15 or newer. Run these commands from any directory.

### 1. Install Homebrew and apply the dotfiles

If Homebrew is missing, install it using the [official instructions](https://brew.sh/),
follow the installer's **Next steps**, and reopen Terminal so `brew` is on your PATH.

```sh
brew install chezmoi
chezmoi init --apply https://github.com/mrleeio/dotfiles.git
```

Choose **personal**, **homelab**, or **work** when prompted.

**Close and reopen Terminal before continuing.** The new shell loads the deployed
PATH and XDG settings automatically.

### 2. Install applications and plugins

```sh
brew bundle --file="$(chezmoi source-path)/Brewfile"
```

After the bundle finishes successfully, install the pinned shell/Neovim plugins
and all configured Tree-sitter parsers:

```sh
vim-up
```

### 3. Reopen Terminal and set up accounts

Close and reopen Terminal again to load the newly installed shell tools and plugins.
Then open 1Password:

```sh
open -a 1Password
```

In 1Password, sign in, unlock your vault, and enable the SSH agent under Developer
settings. Make the profile's SSH key available and register its public key with
your Git hosting account for authentication and signing; see
[Git authentication and signing](docs/git-signing.md). Sign in to the other apps
as needed. Account setup and permissions remain interactive.

These are explicit setup commands.
Normal chezmoi applies and shell/editor startup do not install dependencies.
Existing plugin directories are kept unchanged; see [dependency setup](docs/dependencies.md)
for updating their pinned revisions. Project runtime versions are selected separately
with mise in each project.

## Updates

Pull and apply configuration changes:

```sh
chezmoi update
```

To update Homebrew and upgrade installed software, run:

```sh
brew-up
```

To install newly added Brewfile entries, run
`brew bundle --file="$(chezmoi source-path)/Brewfile"`.
`chezmoi update` does not update packages or plugin checkouts.

## Machine profiles

All profiles share the same Claude sandbox policy. Git identity and Claude
attribution come from `.chezmoidata/machines.yaml`; the work profile also sets
its corporate CA path and SSH host mappings.

All profiles keep Atuin history local, with sync and update checks disabled.

See [Claude Code policy](docs/claude.md) and [Codex policy](docs/codex.md) for
sandbox boundaries, credential restrictions, and verification. Both agents use
`.chezmoitemplates/agent-instructions.md` as their global instruction source.

Profile data is in `.chezmoidata/machines.yaml`. To change your machine name after init:

```sh
# Edit the cached config
$EDITOR ~/.config/chezmoi/chezmoi.toml
# Change machine_name = "personal" to your profile
```

## Neovim

Uses [mini.nvim](https://github.com/echasnovski/mini.nvim) as the plugin/UI framework with native LSP.

**LSP servers** (install separately; included in the Brewfile): gopls, lua_ls, pyright, ruby_lsp, ts_ls

**Key bindings**: `<leader>` is **Space**. Plugin and LSP bindings require their
respective dependencies.

| Key | Action |
|-----|--------|
| `<leader>f` + `f/g/b/h` | Find files / grep / buffers / help |
| `<leader>e` | File explorer |
| `gd` / `gr` / `gI` | Go to definition / references / implementation |
| `K` | Hover docs |
| `<leader>ca` / `<leader>rn` | Code action / rename |
| `Ctrl-hjkl` | Window navigation |
| `Shift-hl` | Previous/next buffer |

**Plugins and Tree-sitter parsers** are installed separately. Startup loads only
existing dependencies; see [dependency setup](docs/dependencies.md).

## Local overrides

- Git reads `~/.gitconfig.local` after the shared configuration. Change local
  preferences with `git config --file ~/.gitconfig.local KEY VALUE` rather than
  editing the managed `~/.gitconfig`. Single-valued options use the later value;
  multi-valued options can accumulate according to Git's rules.
- Ghostty loads an optional `~/.config/ghostty/config.local` after the shared
  configuration. Put local font sizes, themes, and other preferences there.

These files are excluded from chezmoi management and are never created or
replaced by this repo. Missing override files are fine.

## Shell history

Zsh stores history in `~/.zsh_history`. Atuin provides local history search with
automatic sync and update checks disabled.

## Docs

- [Atuin local history](docs/atuin.md) — Local-only history configuration
- [Git authentication and signing](docs/git-signing.md) — 1Password SSH agent and profile identities
- [Dependency setup](docs/dependencies.md) — Explicit installation and updates
- [Neovim](docs/neovim.md) — Plugin architecture, key bindings, adding LSP servers

## Structure

```
.chezmoidata/          Machine profile data
.chezmoitemplates/     Shared configuration templates
dot_config/            ~/.config/ (nvim, atuin, ghostty, starship, mise)
dot_claude/            Claude Code settings
dot_codex/             Codex settings, instructions, and command rules
private_dot_ssh/       SSH host config and public signing information
Brewfile              Optional software inventory (not deployed)
dependencies.json     Plugin revisions and install paths (not deployed)
docs/                 Setup and configuration reference
tests/                Isolated configuration validation
.github/workflows/    CI validation
```

## Validation

Run `CHEZMOI=chezmoi python3 tests/validate.py` with Python 3.11 or newer.
The tests render and apply all profiles with Apple Silicon and Intel template
values in temporary homes. They verify syntax, local overrides, preservation of
app-owned state, and repeatable applies, and reject provisioning hooks or encrypted
credential files. CI runs these checks on macOS; this is configuration validation,
not a full application or hardware compatibility test.
