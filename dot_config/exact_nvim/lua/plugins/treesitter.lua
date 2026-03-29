return {
  "nvim-treesitter/nvim-treesitter",
  build = ":TSUpdate",
  event = { "BufReadPost", "BufNewFile" },
  opts = {
    ensure_installed = {
      "bash", "css", "go", "html", "javascript", "json",
      "lua", "markdown", "python", "ruby", "toml",
      "tsx", "typescript", "yaml",
    },
    highlight = { enable = true },
    indent = { enable = true },
  },
  main = "nvim-treesitter.configs",
}
