return {
  { "windwp/nvim-autopairs", event = "InsertEnter", opts = {} },
  { "kylechui/nvim-surround", event = "VeryLazy", opts = {} },
  { "lewis6991/gitsigns.nvim", event = "BufReadPre", opts = {} },
  {
    "nvim-tree/nvim-tree.lua",
    cmd = "NvimTreeToggle",
    keys = { { "<leader>e", "<cmd>NvimTreeToggle<cr>", desc = "File explorer" } },
    opts = {},
  },
}
