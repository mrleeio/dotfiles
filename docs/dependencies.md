# Optional dependency installation

The repository applies configuration only. Shell and Neovim startup never clone,
fetch, check out, or install missing dependencies. Basic shell and editor settings
work without plugins; features become available after their dependencies exist.

After `chezmoi apply`, reopen your zsh terminal and run:

```sh
vim-up
```

This explicit helper installs missing shell and Neovim plugin checkouts from
`dependencies.json` at their pinned revisions, then installs the Tree-sitter
parsers listed in Neovim's `lua/treesitter_languages.lua`. It waits for parser
installation and returns a nonzero status on failure. Run it after installing
the Brewfile dependencies. Existing plugin directories are left unchanged,
including local edits; this is setup, not a plugin upgrade command.

The manifest records Git repository URLs, immutable revisions, and installation
paths. `vim-up` reads it from `chezmoi source-path`; it is not deployed into your
home directory. Paths use the standard XDG locations configured by this repository.

For updates, review the upstream diff, update the manifest, and explicitly fetch
and check out the desired revision outside normal shell/editor startup. Pins are
an installation reference, not enforced against existing checkouts at runtime.

Tree-sitter parsers are also installed explicitly. With nvim-treesitter installed,
run `:lua require('nvim-treesitter').install({ 'lua', 'ruby', 'python' })` for the
languages you use. Missing parsers fall back to ordinary syntax highlighting.

The optional `Brewfile` lists application and language-server dependencies. Run
`brew bundle --file=Brewfile` explicitly from the repository when desired.

Neovim's external formatters are StyLua, Ruff, goimports, gofmt (provided by Go),
and Prettier. They are included in the Brewfile. Ruby formatting uses the Ruby
LSP's project-supported formatter.

mise pins versions selected by `mise use` and maintains project lockfiles. Python
and Ruby prefer precompiled binaries and may compile from source when unavailable.
