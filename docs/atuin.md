# Atuin local history

All profiles use Atuin for local history search. In `~/.config/atuin/config.toml`:

- `auto_sync = false` disables automatic history synchronization.
- `update_check = false` disables update checks.
- `sync_address = "http://127.0.0.1:1"` prevents manual sync/login commands from
  falling back to the public service.

Zsh loads Atuin's shell integration when the executable is available. Local
history search works without an account.

Ctrl-R and Up-arrow search only commands recorded in the exact current directory.
Both filter defaults are `directory`, and `[search].filters = ["directory"]`
prevents cycling to broader history. Recording is unchanged. To allow occasional
global searches, remove the `[search]` table while keeping the directory defaults.

See the [Atuin configuration reference](https://docs.atuin.sh/main/configuration/config/).
