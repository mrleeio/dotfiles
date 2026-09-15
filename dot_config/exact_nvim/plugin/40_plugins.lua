local plugins = require('local_plugins')
local add, now, later = plugins.add, plugins.now, plugins.later

-- Highlighting uses only parsers already installed on this machine.
now(function()
  add({ source = 'nvim-treesitter/nvim-treesitter' })
  if add({ source = 'nvim-treesitter/nvim-treesitter-textobjects' }) then
    require('nvim-treesitter-textobjects').setup({ select = { lookahead = true } })
    for keys, capture in pairs({
      af = '@function.outer', ['if'] = '@function.inner',
      ac = '@class.outer', ic = '@class.inner',
    }) do
      vim.keymap.set({ 'x', 'o' }, keys, function()
        require('nvim-treesitter-textobjects.select').select_textobject(capture, 'textobjects')
      end, { desc = 'Select ' .. capture })
    end
  end

  local languages = require('treesitter_languages')

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
    callback = function(ev)
      local lang = vim.treesitter.language.get_lang(vim.bo[ev.buf].filetype)
      if lang and pcall(vim.treesitter.language.inspect, lang) then
        vim.treesitter.start(ev.buf, lang)
      end
    end,
  })
end)

-- ============================================================
-- LSP
-- ============================================================

later(function()
  if not add({ source = 'neovim/nvim-lspconfig' }) then return end

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

  -- Inherit nvim-lspconfig defaults; after/lsp/*.lua holds only overrides.
  -- Servers are installed via Homebrew (see Brewfile).
  vim.lsp.enable({ 'ruby_lsp', 'gopls', 'pyright', 'ts_ls', 'lua_ls' })
end)

-- ============================================================
-- Formatting
-- ============================================================

later(function()
  if not add({ source = 'stevearc/conform.nvim' }) then return end

  require('conform').setup({
    formatters_by_ft = {
      lua = { 'stylua' },
      python = { 'ruff_format' },
      go = { 'goimports', 'gofmt' },
      javascript = { 'prettier' },
      javascriptreact = { 'prettier' },
      typescript = { 'prettier' },
      typescriptreact = { 'prettier' },
      json = { 'prettier' },
      css = { 'prettier' },
      html = { 'prettier' },
      markdown = { 'prettier' },
      yaml = { 'prettier' },
    },
    format_on_save = {
      lsp_format = 'fallback',
      timeout_ms = 500,
    },
  })
end)
