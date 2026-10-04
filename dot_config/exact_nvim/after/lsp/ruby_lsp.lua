-- Ruby LSP runs the project's Bundler setup (Gemfile code, bundle install) on
-- start, so it only attaches in directories trusted with :trust.
return {
  root_dir = function(bufnr, on_dir)
    local root = vim.fs.root(bufnr, { 'Gemfile', 'gems.rb', '.git' })
    if root and vim.secure.read(root) then
      on_dir(root)
    end
  end,
  -- Launch from the project root so mise selects the project's Ruby and its ruby-lsp gem.
  cmd = function(dispatchers, config)
    return vim.lsp.rpc.start({ 'mise', 'exec', '--', 'ruby-lsp' }, dispatchers, { cwd = config.root_dir })
  end,
  reuse_client = function(client, config)
    return client.config.root_dir == config.root_dir
  end,
}
