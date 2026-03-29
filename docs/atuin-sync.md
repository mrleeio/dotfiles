# Atuin sync

Shell history is synced between machines using a self-hosted [atuin](https://atuin.sh/) server running on the homelab. History is end-to-end encrypted — the server stores ciphertext only.

## Architecture

```
personal ──────► homelab (192.168.1.237:8888) ◄────── homelab
                        atuin server
                        SQLite database

work (no sync)
```

| Profile | Behavior |
|---------|----------|
| **homelab** | Runs the atuin server via LaunchAgent. Syncs to localhost. |
| **personal** | Syncs to `http://192.168.1.237:8888` |
| **work** | Sync disabled (`auto_sync = false`) |

## Server setup (homelab)

The server is configured automatically by chezmoi on the homelab profile.

**Config file**: `~/.config/atuin/server.toml`

```toml
host = "0.0.0.0"
port = 8888
open_registration = true
db_uri = "sqlite:///Users/mrlee/.config/atuin/server.db"
```

**LaunchAgent**: `~/Library/LaunchAgents/com.atuin.server.plist` starts the server on login and keeps it alive.

After `chezmoi apply`, verify the server is running:

```sh
launchctl list | grep atuin
# Should show com.atuin.server with a PID

curl http://localhost:8888
# Should return a response
```

### Server logs

```sh
cat /tmp/atuin-server.log
cat /tmp/atuin-server.err
```

### Restart the server

```sh
launchctl kickstart -k gui/$(id -u)/com.atuin.server
```

## Client setup

After the server is running on the homelab, register and log in from each machine.

### 1. Register (run once, on any machine)

```sh
atuin register -u <username> -p <password> -e <email>
```

This creates an account and generates a local encryption key.

### 2. Get the encryption key

On the machine where you registered:

```sh
atuin key --base64
```

Save this key — you'll need it to log in from other machines.

### 3. Log in from other machines

```sh
atuin login -u <username> -p <password> -k <base64-key>
```

### 4. Verify sync

```sh
atuin sync
atuin status
```

## Disable sync on work profile

The work profile has `auto_sync = false` in `~/.config/atuin/config.toml`. Atuin still works locally for history search, it just doesn't communicate with the server.

To temporarily enable sync on work (e.g., on a trusted network):

```sh
atuin sync  # Manual one-off sync
```

## Disable open registration

After all machines are registered, disable new signups on the homelab:

Edit `~/.config/atuin/server.toml`:

```toml
open_registration = false
```

Then restart the server:

```sh
launchctl kickstart -k gui/$(id -u)/com.atuin.server
```

## Troubleshooting

**Server not starting**: Check logs at `/tmp/atuin-server.err`. Common issues:
- Port 8888 already in use
- SQLite database directory doesn't exist

**Can't connect from personal**: Verify the homelab is reachable:
```sh
curl http://192.168.1.237:8888
```

**Sync failing**: Check you're logged in:
```sh
atuin status
```

If the session expired, log in again with `atuin login`.

**Reset and start fresh**:
```sh
# On the server (homelab)
rm ~/.config/atuin/server.db
launchctl kickstart -k gui/$(id -u)/com.atuin.server

# On clients
atuin register -u <username> -p <password> -e <email>
```
