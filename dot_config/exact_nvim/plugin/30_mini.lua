local plugins = require('local_plugins')
local add, now, later = plugins.add, plugins.now, plugins.later

if not add({ source = 'echasnovski/mini.nvim' }) then return end
local has_theme = add({ source = 'catppuccin/nvim', name = 'catppuccin' })

-- ============================================================
-- NOW: things needed before first render
-- ============================================================

now(function()
  if has_theme then vim.cmd.colorscheme('catppuccin') end
end)

now(function()
  -- Icons (must be before statusline, notify, etc.)
  require('mini.icons').setup()
  MiniIcons.mock_nvim_web_devicons()
end)

now(function()
  -- Notifications
  require('mini.notify').setup()
  vim.notify = MiniNotify.make_notify()
end)

now(function()
  -- Statusline
  require('mini.statusline').setup()
end)

-- ============================================================
-- LATER: deferred until after first render
-- ============================================================

later(function()
  -- Completion (LSP-based with buffer fallback)
  require('mini.completion').setup({
    lsp_completion = {
      source_func = 'omnifunc',
      auto_setup = false,
    },
  })
  vim.api.nvim_create_autocmd('LspAttach', {
    group = vim.api.nvim_create_augroup('mini-completion-attach', { clear = true }),
    callback = function(event)
      vim.bo[event.buf].omnifunc = 'v:lua.MiniCompletion.completefunc_lsp'
    end,
  })
end)

later(function()
  -- Snippets
  add({ source = 'rafamadriz/friendly-snippets' })
  require('mini.snippets').setup({
    snippets = {
      -- Load friendly-snippets if available
      require('mini.snippets').gen_loader.from_lang(),
    },
  })
end)

later(function()
  -- Fuzzy picker
  require('mini.pick').setup()
  vim.keymap.set('n', '<leader>ff', '<cmd>Pick files<cr>', { desc = 'Find files' })
  vim.keymap.set('n', '<leader>fg', '<cmd>Pick grep_live<cr>', { desc = 'Live grep' })
  vim.keymap.set('n', '<leader>fb', '<cmd>Pick buffers<cr>', { desc = 'Buffers' })
  vim.keymap.set('n', '<leader>fh', '<cmd>Pick help<cr>', { desc = 'Help tags' })
end)

later(function()
  -- File explorer
  require('mini.files').setup()
  vim.keymap.set('n', '<leader>e', function() MiniFiles.open() end, { desc = 'File explorer' })
end)

later(function()
  -- Surround operations (sa, sd, sr)
  require('mini.surround').setup()
end)

later(function()
  -- Auto-close pairs
  require('mini.pairs').setup()
end)

later(function()
  -- Git integration (hunks, blame, log)
  require('mini.git').setup()
end)

later(function()
  -- Diff overlay (shows git diff in buffer)
  require('mini.diff').setup()
end)

later(function()
  -- Comment toggling (gc, gcc)
  require('mini.comment').setup()
end)
