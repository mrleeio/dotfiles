# Neovim

Neovim config built on [mini.nvim](https://github.com/echasnovski/mini.nvim) as the core framework, with native LSP and tree-sitter.

## Architecture

```
init.lua                    Bootstrap mini.deps (auto-installs mini.nvim)
lua/config/
  options.lua               Editor settings (tabs, search, appearance)
  keymaps.lua               Key bindings (leader = Space)
  autocmds.lua              Auto-commands (yank highlight, trailing whitespace)
plugin/
  30_mini.lua               Mini modules (UI, completion, picker, git, etc.)
  40_plugins.lua            Tree-sitter, LSP, formatting, snippets
after/lsp/
  gopls.lua                 Go LSP config
  lua_ls.lua                Lua LSP config
  pyright.lua               Python LSP config
  ruby_lsp.lua              Ruby LSP config
  ts_ls.lua                 TypeScript LSP config
```

## Plugin management: mini.deps

Unlike lazy.nvim or packer, [mini.deps](https://github.com/echasnovski/mini.nvim/blob/main/readmes/mini-deps.md) is minimal and explicit. Key concepts:

- `add()` — declares a dependency (installs if missing, updates rtp)
- `now()` — runs immediately, before first render (colorscheme, statusline, icons)
- `later()` — deferred until after first render (completion, picker, git, etc.)

This split keeps startup fast — only essential UI loads before the first frame.

## Mini modules

Loaded in `plugin/30_mini.lua`:

| Module | Purpose | Loaded |
|--------|---------|--------|
| mini.icons | File/devicons (mocks nvim-web-devicons) | now |
| mini.notify | Notification popups (replaces vim.notify) | now |
| mini.statusline | Statusline | now |
| mini.completion | LSP + buffer completion | later |
| mini.snippets | Snippet engine (loads friendly-snippets) | later |
| mini.pick | Fuzzy finder (files, grep, buffers, help) | later |
| mini.files | File explorer | later |
| mini.surround | Surround operations (ys, ds, cs) | later |
| mini.pairs | Auto-close brackets/quotes | later |
| mini.git | Git hunks, blame, log | later |
| mini.diff | Inline diff overlay | later |
| mini.comment | Comment toggling (gc, gcc) | later |

## Additional plugins

Loaded in `plugin/40_plugins.lua`:

| Plugin | Purpose |
|--------|---------|
| nvim-treesitter | Syntax parsing and highlighting |
| nvim-treesitter-textobjects | Treesitter-aware text objects |
| nvim-lspconfig | LSP server configuration |
| conform.nvim | Format-on-save (LSP fallback, 500ms timeout) |
| friendly-snippets | Snippet library |
| catppuccin/nvim | Colorscheme |

## Tree-sitter

Uses the **main branch** of nvim-treesitter (2024 rewrite), which has a different API:

- No `require('nvim-treesitter.configs').setup()` — that's gone
- Parser install: `require('nvim-treesitter').install(languages)`
- Highlighting: uses Neovim's built-in `vim.treesitter.start()` via autocmd

Parsers auto-install on startup if `tree-sitter-cli` is on PATH.

**Languages**: bash, css, go, html, javascript, json, lua, markdown, python, ruby, toml, tsx, typescript, yaml

## LSP

Servers are installed via **Homebrew** (not Mason). Configured in `after/lsp/*.lua`.

| Server | Languages |
|--------|-----------|
| gopls | Go |
| lua_ls | Lua |
| pyright | Python |
| ruby_lsp | Ruby |
| ts_ls | JavaScript, TypeScript |

Enabled in `plugin/40_plugins.lua` via `vim.lsp.enable()`.

## Key bindings

Leader is **Space**.

### General

| Key | Mode | Action |
|-----|------|--------|
| `Ctrl-hjkl` | Normal | Window navigation |
| `Shift-h` / `Shift-l` | Normal | Previous / next buffer |
| `Esc` | Normal | Clear search highlight |
| `<` / `>` | Visual | Indent and stay in visual mode |
| `J` / `K` | Visual | Move lines down / up |

### Finder (mini.pick)

| Key | Action |
|-----|--------|
| `<leader>ff` | Find files |
| `<leader>fg` | Live grep |
| `<leader>fb` | Buffers |
| `<leader>fh` | Help tags |

### File explorer

| Key | Action |
|-----|--------|
| `<leader>e` | Open mini.files |

### LSP (active in buffers with LSP attached)

| Key | Action |
|-----|--------|
| `gd` | Go to definition |
| `gr` | Go to references |
| `gI` | Go to implementation |
| `K` | Hover documentation |
| `<leader>ca` | Code action |
| `<leader>rn` | Rename symbol |
| `<leader>ds` | Document symbols |

### Surround (mini.surround)

| Key | Action |
|-----|--------|
| `sa` | Add surrounding |
| `sd` | Delete surrounding |
| `sr` | Replace surrounding |

### Comment (mini.comment)

| Key | Action |
|-----|--------|
| `gc` | Toggle comment (visual) |
| `gcc` | Toggle comment (line) |

## Adding a new LSP server

1. Install the server via Homebrew — add it to `.chezmoidata/packages.yaml`
2. Create `dot_config/exact_nvim/after/lsp/<server>.lua` with the server config:

```lua
return {
  cmd = { 'server-binary' },
  filetypes = { 'lang' },
  root_markers = { 'marker-file' },
}
```

3. Add the server name to `vim.lsp.enable()` in `plugin/40_plugins.lua`
4. Add the language to the `languages` table in `plugin/40_plugins.lua` for tree-sitter
