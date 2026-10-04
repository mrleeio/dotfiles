# Atuin local history

All profiles use Atuin for local history search. In `~/.config/atuin/config.toml`:

- `auto_sync = false` disables automatic history synchronization.
- `update_check = false` disables update checks.
- `sync_address = "http://127.0.0.1:1"` prevents manual sync/login commands from
  falling back to the public service.

Zsh loads Atuin's shell integration when the executable is available. Local
history search works without an account.

Ctrl-R searches commands recorded anywhere in the current git repository, and
only the current directory outside one: `[search].filters = ["workspace",
"directory"]` starts with the first filter that applies and limits Ctrl-R to
those two. Up-arrow searches only the current directory
(`filter_mode_shell_up_key_binding = "directory"`). Recording is unchanged. To
allow occasional global searches, add `"global"` to `[search].filters`.

See the [Atuin configuration reference](https://docs.atuin.sh/main/configuration/config/).
