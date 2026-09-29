# Git authentication and commit signing

## SSH authentication

SSH uses the 1Password agent through its macOS socket at
`~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock`.
Enable the SSH agent in 1Password's Developer settings and unlock the app.

Chezmoi manages `~/.config/1Password/ssh/agent.toml`, which lists the 1Password
SSH key items each profile uses, in the order the agent offers them.
This explicit list replaces 1Password's default vault selection. Keep these
item titles synchronized with 1Password if you rename any key. After first
creating the file, lock and unlock 1Password if the keys do not appear.

For GitHub, chezmoi writes the profile's public signing key to `~/.ssh/github.pub`.
This key is also used for GitHub authentication: `IdentityFile` selects the
matching key in 1Password, and `IdentitiesOnly yes` prevents unrelated agent keys
from being offered. No local private-key file is required. Register the public
key as an **Authentication Key** in GitHub as well as a **Signing Key**.

On the work profile that key is `Gen 2 Fund SSH Key` (RSA), and it is also used
for Azure DevOps (`ssh.dev.azure.com`), selected through `~/.ssh/github.pub`
with `IdentitiesOnly yes`. Register that public key in Azure DevOps as an SSH key.

Verify GitHub access without SSH command overrides:

```sh
ssh -T git@github.com
git ls-remote git@github.com:mrleeio/dotfiles.git HEAD
```

GitHub's successful `ssh -T` greeting exits with status 1 because it does not
provide an interactive shell.

See [1Password's SSH configuration guide](https://www.1password.dev/ssh/agent/advanced).

## Commit signing

Each profile's `signingkey` in `.chezmoidata/machines.yaml` selects its SSH
signing key held in 1Password. The personal and homelab profiles use
`Michael Lee SSH Key`; the work profile signs as `mlee@gen2fund.com` with
`Gen 2 Fund SSH Key`. The repository stores only public keys. Git invokes
`/Applications/1Password.app/Contents/MacOS/op-ssh-sign`; private signing material
is not exported to this repository.

Install and unlock 1Password, make the signing key available there, and apply the
configuration. Authorize the signing request when 1Password prompts you.

```sh
git commit -S -m "fix: describe the change"
git log --show-signature -1
```

`~/.ssh/allowed_signers` maps the profile email to the configured public key for
local verification. Add this public key as a **Signing Key** in your Git hosting
account to enable hosted signature verification.

For future signing-key rotation, update `signingkey` for each applicable profile,
make the new private key available in 1Password, and reapply the configuration.
Keep historical public keys in a separate verification trust file if you need to
verify commits made with retired keys.
