local opt = vim.opt

-- Line numbers
opt.number = true
opt.relativenumber = true

-- Tabs & indentation
opt.tabstop = 2
opt.shiftwidth = 2
opt.softtabstop = 2
opt.expandtab = true
opt.smartindent = true

-- Line wrapping
opt.wrap = false

-- Search
opt.ignorecase = true
opt.smartcase = true
opt.hlsearch = true
opt.incsearch = true

-- Appearance
opt.termguicolors = true
opt.signcolumn = "yes"
opt.cursorline = true
opt.colorcolumn = "80"
opt.scrolloff = 8

-- Splits
opt.splitbelow = true
opt.splitright = true

-- Clipboard
opt.clipboard = "unnamedplus"

-- Persistence
opt.undofile = true
opt.swapfile = false
opt.backup = false

-- Performance
opt.updatetime = 250
opt.timeoutlen = 300

-- Completion
opt.completeopt = { "menu", "menuone", "noselect" }
