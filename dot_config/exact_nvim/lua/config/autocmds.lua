local autocmd = vim.api.nvim_create_autocmd
local augroup = vim.api.nvim_create_augroup

-- Highlight on yank
autocmd("TextYankPost", {
  group = augroup("highlight-yank", { clear = true }),
  callback = function()
    vim.highlight.on_yank()
  end,
})

-- Remove trailing whitespace on save
autocmd("BufWritePre", {
  group = augroup("trim-whitespace", { clear = true }),
  pattern = "*",
  command = [[%s/\s\+$//e]],
})

-- Go uses tabs
autocmd("FileType", {
  group = augroup("go-indent", { clear = true }),
  pattern = "go",
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.expandtab = false
  end,
})
