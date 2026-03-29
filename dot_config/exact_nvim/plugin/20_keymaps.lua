vim.g.mapleader = ' '
vim.g.maplocalleader = ' '

local map = vim.keymap.set

-- Window navigation
map('n', '<C-h>', '<C-w>h')
map('n', '<C-j>', '<C-w>j')
map('n', '<C-k>', '<C-w>k')
map('n', '<C-l>', '<C-w>l')

-- Buffer navigation
map('n', '<S-h>', '<cmd>bprevious<cr>')
map('n', '<S-l>', '<cmd>bnext<cr>')

-- Clear search highlight
map('n', '<Esc>', '<cmd>nohlsearch<cr>')

-- Better indenting (stay in visual mode)
map('v', '<', '<gv')
map('v', '>', '>gv')

-- Move lines in visual mode
map('v', 'J', ":m '>+1<cr>gv=gv")
map('v', 'K', ":m '<-2<cr>gv=gv")

-- Autocmds
local augroup = vim.api.nvim_create_augroup
local autocmd = vim.api.nvim_create_autocmd

autocmd('TextYankPost', {
  group = augroup('highlight-yank', { clear = true }),
  callback = function() vim.highlight.on_yank() end,
})

autocmd('BufWritePre', {
  group = augroup('trim-whitespace', { clear = true }),
  pattern = '*',
  command = [[%s/\s\+$//e]],
})

autocmd('FileType', {
  group = augroup('go-indent', { clear = true }),
  pattern = 'go',
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.expandtab = false
  end,
})
