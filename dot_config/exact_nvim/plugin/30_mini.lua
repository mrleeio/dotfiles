local add, now, later = MiniDeps.add, MiniDeps.now, MiniDeps.later

-- Add mini.nvim (already bootstrapped in init.lua, this is a no-op but keeps deps explicit)
add('echasnovski/mini.nvim')

-- Catppuccin must be add()-ed here, before the now() block that applies it.
-- add() is synchronous: it installs if missing, then updates rtp immediately.
add({ source = 'catppuccin/nvim', name = 'catppuccin' })

-- ============================================================
-- NOW: things needed before first render
-- ============================================================

now(function()
  vim.cmd.colorscheme('catppuccin')
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
end)

later(function()
  -- Snippets
  require('mini.snippets').setup({
    snippets = {
      -- Load friendly-snippets if available
      require('mini.snippets').gen_loader.from_runtime('snippets'),
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
  -- Surround operations (ys, ds, cs)
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
