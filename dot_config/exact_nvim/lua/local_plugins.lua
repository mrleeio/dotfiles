-- Load existing native packages without downloading or changing checkouts.
local M = {}
function M.add(spec)
  local name = spec.name or spec.source:match('[^/]+$')
  local root = vim.fn.stdpath('data') .. '/site/pack/deps/'
  if not vim.uv.fs_stat(root .. 'start/' .. name) and not vim.uv.fs_stat(root .. 'opt/' .. name) then
    return false
  end
  vim.cmd.packadd(name)
  return true
end
function M.now(callback) callback() end
function M.later(callback) vim.schedule(callback) end
return M
