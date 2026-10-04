# dotfiles

Machine-agnostic dotfiles managed with [chezmoi](https://www.chezmoi.io/), supporting two profiles: **personal** and **work**.

## What's included

| Category | Tools |
|----------|-------|
| Shell | zsh, [starship](https://starship.rs/), [atuin](https://atuin.sh/), [zoxide](https://github.com/ajeetdsouza/zoxide) |
| Editor | [Neovim](https://neovim.io/) configuration (mini.nvim + LSP) |
| Terminal | [ghostty](https://ghostty.org/) with Catppuccin theme |
| Git | Profile-specific identity, SSH authentication, and commit and tag signing through 1Password |
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

Choose **personal** or **work** when prompted.

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

Git identity comes from `.chezmoidata/machines.yaml`; the work profile also sets
its corporate CA path.

All profiles keep Atuin history local, with sync and update checks disabled.

Profile data is in `.chezmoidata/machines.yaml`. To change your machine name after init:

```sh
# Edit the cached config
$EDITOR ~/.config/chezmoi/chezmoi.toml
# Change machine_name = "personal" to your profile
```

## Neovim

Uses [mini.nvim](https://github.com/echasnovski/mini.nvim) as the plugin/UI framework with native LSP.

**LSP servers** (install separately): gopls, lua_ls, pyright, and ts_ls are in the
Brewfile; ruby_lsp is a gem in each mise-managed Ruby and starts only in
trusted projects (see [Neovim](docs/neovim.md#ruby-lsp)).

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

Zsh stores up to 32,768 entries in `~/.zsh_history`. Commands typed with a
leading space are not saved, which keeps one-off secrets out of history. Atuin
provides local history search with automatic sync and update checks disabled.

## Shell helpers

| Command | Action |
|---------|--------|
| `g` | `git status`, or `git` with arguments |
| `mcd DIR` | Create a directory and change into it |
| `...`, `....` | Go up two or three directories |
| `-` | Return to the previous directory |
| `cd -<Tab>` | Pick from recently visited directories |
| `whats-in-port PORT` | List processes listening on a TCP port |
| `clear-port PORT` | Stop every process listening on a TCP port |
| `brew-up` | Update Homebrew and upgrade installed software |
| `vim-up` | Install pinned plugins and Tree-sitter parsers |

Completions are rebuilt at most once a day and cached in `~/.cache/zsh`;
`brew-up` and `vim-up` clear the cache so new completions load in the next shell.

## Git defaults

Beyond identity and signing, `~/.gitconfig` follows settings recommended by Git's
core developers: histogram diffs, `zdiff3` conflict markers, remembered conflict
resolutions (`rerere`), auto-stash and stacked-branch updates on rebase, the diff
shown while writing commit messages, branches sorted by recent commits, and
`help.autocorrect = prompt`. `push.followTags` pushes annotated tags with their
commits, and `fetch.pruneTags` deletes local tags that no longer exist on the
remote, so push any local-only tags you want to keep. Tags are signed like
commits; `git tag NAME` creates a signed, annotated tag and asks for a message.

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
