# Neovim

Neovim config built on [mini.nvim](https://github.com/echasnovski/mini.nvim) as the core framework, with native LSP and tree-sitter.

## Architecture

```
init.lua                    Configuration entry point (no bootstrap)
lua/local_plugins.lua       Loads installed native packages only
plugin/
  10_options.lua            Editor settings
  20_keymaps.lua            Key bindings and auto-commands (leader = Space)
  30_mini.lua               Mini modules (UI, completion, picker, git, etc.)
  40_plugins.lua            Tree-sitter, LSP, formatting
after/lsp/
  gopls.lua                 Go LSP config
  lua_ls.lua                Lua LSP config
  pyright.lua               Python LSP config
```

## Plugin loading

The local package loader uses Neovim's native `packadd` for packages already
installed in the directories listed in `dependencies.json`. It performs no
installation or updates. Missing plugins are skipped; core editor settings still
load. See [dependency setup](dependencies.md) for explicit installation.

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
| mini.surround | Surround operations (sa, sd, sr) | later |
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
| conform.nvim | External formatters on save (LSP fallback, 500ms timeout) |
| friendly-snippets | Snippet library (loaded in `30_mini.lua` before snippet setup) |
| catppuccin/nvim | Colorscheme |

## Tree-sitter

Uses a **pinned revision from the main branch** of nvim-treesitter (2024 rewrite), which has a different API:

- No `require('nvim-treesitter.configs').setup()` — that's gone
- Parser install: `require('nvim-treesitter').install(languages)`
- Highlighting: uses Neovim's built-in `vim.treesitter.start()` via autocmd

Parsers are installed explicitly; startup only enables available parsers.

**Languages**: bash, css, go, html, javascript, json, lua, markdown, python, ruby, toml, tsx, typescript, yaml

## LSP

Servers are installed via **Homebrew** (not Mason). Command, filetype, and project
root defaults come from nvim-lspconfig. Only intentional settings overrides live
in `after/lsp/*.lua`; Ruby and TypeScript use the upstream configuration directly.

| Server | Languages |
|--------|-----------|
| gopls | Go |
| lua_ls | Lua |
| pyright | Python |
| ruby_lsp | Ruby |
| ts_ls | JavaScript, TypeScript |

Enabled in `plugin/40_plugins.lua` via `vim.lsp.enable()`.

mini.completion sets its LSP omnifunc on `LspAttach`. mini.snippets discovers
friendly-snippets by the current language with `gen_loader.from_lang()`.

## Formatting

Conform formats on save with a 500ms timeout:

| Files | Formatter |
|-------|-----------|
| Lua | StyLua |
| Python | Ruff (`ruff_format`) |
| Go | goimports, then gofmt |
| JavaScript/TypeScript (including JSX/TSX), JSON, CSS, HTML, Markdown, YAML | Prettier |
| Other files, including Ruby | Attached LSP formatting, when supported |

The executables are listed in `Brewfile`; install them explicitly as described in
[dependency setup](dependencies.md). If no configured external formatter is
available, Conform falls back to LSP formatting. Without either, files are not
formatted. Project formatter configuration remains authoritative.

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

### Tree-sitter textobjects

Available in Visual and Operator-pending modes when the parser and queries exist:

| Key | Selection |
|-----|-----------|
| `af` / `if` | Entire function / function body |
| `ac` / `ic` | Entire class / class body |

For example, `dif` deletes the function body. Selection can look ahead to the next
matching object.

### Comment (mini.comment)

| Key | Action |
|-----|--------|
| `gc` | Toggle comment (visual) |
| `gcc` | Toggle comment (line) |

## Adding a new LSP server

1. Install the server via Homebrew — add it to `Brewfile`
2. If nvim-lspconfig provides the server, inherit its defaults and create
   `dot_config/exact_nvim/after/lsp/<server>.lua` only for intentional overrides.
   For a server without an upstream config, define its command and filetypes:

```lua
return {
  cmd = { 'server-binary' },
  filetypes = { 'lang' },
  root_markers = { 'marker-file' },
}
```

3. Add the server name to `vim.lsp.enable()` in `plugin/40_plugins.lua`
4. Add the language to `lua/treesitter_languages.lua` and run `vim-up` to install its parser
