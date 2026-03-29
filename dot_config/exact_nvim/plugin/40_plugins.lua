local add, now, later = MiniDeps.add, MiniDeps.now, MiniDeps.later

-- ============================================================
-- Syntax highlighting
--
-- nvim-treesitter main branch (2024 rewrite):
--   - require('nvim-treesitter.configs').setup() no longer exists
--   - ensure_installed / highlight.enable are gone
--   - Use require('nvim-treesitter').install() for parsers
--   - Use vim.treesitter.start() (Neovim built-in) for highlighting
--   - Must use now(), not later() — treesitter does not support lazy-loading
-- ============================================================

now(function()
  add({
    source = 'nvim-treesitter/nvim-treesitter',
    hooks = { post_checkout = function() vim.cmd('TSUpdate') end },
  })
  add('nvim-treesitter/nvim-treesitter-textobjects')

  local languages = {
    'bash', 'css', 'go', 'html', 'javascript', 'json',
    'lua', 'markdown', 'python', 'ruby', 'toml',
    'tsx', 'typescript', 'yaml',
  }

  -- Install any missing parsers, but only if the tree-sitter CLI is available.
  -- Uses vim.treesitter.language.inspect() — more reliable than checking rtp files.
  if vim.fn.executable('tree-sitter') == 1 then
    local missing = vim.tbl_filter(function(lang)
      return not pcall(vim.treesitter.language.inspect, lang)
    end, languages)
    if #missing > 0 then
      require('nvim-treesitter').install(missing)
    end
  end

  -- Enable highlighting per buffer via Neovim's built-in treesitter API
  local filetypes = {}
  for _, lang in ipairs(languages) do
    for _, ft in ipairs(vim.treesitter.language.get_filetypes(lang)) do
      table.insert(filetypes, ft)
    end
  end
  vim.api.nvim_create_autocmd('FileType', {
    group = vim.api.nvim_create_augroup('treesitter-start', { clear = true }),
    pattern = filetypes,
    callback = function(ev) vim.treesitter.start(ev.buf) end,
  })
end)

-- ============================================================
-- LSP
-- ============================================================

later(function()
  add('neovim/nvim-lspconfig')

  -- Enable LSP servers (configured in after/lsp/*.lua)
  -- Servers are installed via Homebrew (see .chezmoidata/packages.yaml)
  vim.lsp.enable({ 'ruby_lsp', 'gopls', 'pyright', 'ts_ls', 'lua_ls' })

  -- Shared on_attach keymaps
  vim.api.nvim_create_autocmd('LspAttach', {
    group = vim.api.nvim_create_augroup('lsp-attach-keymaps', { clear = true }),
    callback = function(event)
      local map = function(keys, func, desc)
        vim.keymap.set('n', keys, func, { buffer = event.buf, desc = desc })
      end
      map('gd', vim.lsp.buf.definition, 'Go to definition')
      map('gr', vim.lsp.buf.references, 'Go to references')
      map('gI', vim.lsp.buf.implementation, 'Go to implementation')
      map('K', vim.lsp.buf.hover, 'Hover documentation')
      map('<leader>ca', vim.lsp.buf.code_action, 'Code action')
      map('<leader>rn', vim.lsp.buf.rename, 'Rename')
      map('<leader>ds', vim.lsp.buf.document_symbol, 'Document symbols')
    end,
  })
end)

-- ============================================================
-- Formatting
-- ============================================================

later(function()
  add('stevearc/conform.nvim')

  require('conform').setup({
    format_on_save = {
      lsp_format = 'fallback',
      timeout_ms = 500,
    },
  })
end)

-- ============================================================
-- Snippets library
-- ============================================================

later(function()
  add('rafamadriz/friendly-snippets')
end)
