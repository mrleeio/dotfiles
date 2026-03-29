vim.g.mapleader = " "
vim.g.maplocalleader = " "

local map = vim.keymap.set

-- Window navigation
map("n", "<C-h>", "<C-w>h")
map("n", "<C-j>", "<C-w>j")
map("n", "<C-k>", "<C-w>k")
map("n", "<C-l>", "<C-w>l")

-- Buffer navigation
map("n", "<S-h>", "<cmd>bprevious<cr>")
map("n", "<S-l>", "<cmd>bnext<cr>")

-- Clear search highlight
map("n", "<Esc>", "<cmd>nohlsearch<cr>")

-- Better indenting (stay in visual mode)
map("v", "<", "<gv")
map("v", ">", ">gv")

-- Move lines
map("v", "J", ":m '>+1<cr>gv=gv")
map("v", "K", ":m '<-2<cr>gv=gv")

-- Lazy dashboard
map("n", "<leader>l", "<cmd>Lazy<cr>")
