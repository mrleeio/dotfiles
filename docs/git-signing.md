# Git commit signing with SSH keys

All commits and tags are signed using SSH keys managed by chezmoi. Each machine profile has its own key pair, stored encrypted in the repo with age.

## How it works

```
git commit ──► ssh-keygen (built-in) ──► signs with SSH private key from ~/.ssh/
```

Relevant config in `~/.gitconfig`:

```ini
[commit]
  gpgsign = true
[gpg]
  format = ssh
[gpg "ssh"]
  allowedSignersFile = ~/.ssh/allowed_signers
[user]
  signingkey = ssh-ed25519 AAAA...
```

## Key layout

| Profile | Key file | Type | Used for |
|---------|----------|------|----------|
| personal / homelab | `id_ed25519_personal` | Ed25519 | GitHub auth + signing |
| work | `id_ed25519_work` | Ed25519 | GitHub auth + signing |
| work | `id_rsa_work` | RSA-4096 | Azure DevOps auth only |

Azure DevOps requires RSA keys for SSH authentication — Ed25519 is not supported. ADO also does not verify commit signatures (no "Verified" badge). GitHub supports both Ed25519 auth and SSH signature verification.

## Setup on a new machine

1. Install chezmoi and set up age encryption (see main README)
2. Run `chezmoi apply` — this deploys the correct keys for your profile and loads them into ssh-agent
3. Verify:

```sh
# Check keys are loaded
ssh-add -l

# Test GitHub auth
ssh -T git@github.com

# Test ADO auth (work only)
ssh -T git@ssh.dev.azure.com

# Test signing
git commit --allow-empty -m "test signing"
git log --show-signature -1
```

## Generating new keys

If you need to generate fresh keys:

```sh
# Personal — Ed25519
ssh-keygen -t ed25519 -C "michael@mrlee.io" -f ~/.ssh/id_ed25519_personal

# Work — Ed25519 for GitHub
ssh-keygen -t ed25519 -C "mlee@gen2fund.com" -f ~/.ssh/id_ed25519_work

# Work — RSA for Azure DevOps
ssh-keygen -t rsa-sha2-512 -b 4096 -C "mlee@gen2fund.com" -f ~/.ssh/id_rsa_work
```

Then:

1. Add the Ed25519 public keys to GitHub as both **Authentication** and **Signing** keys (Settings > SSH and GPG keys)
2. Add the RSA public key to Azure DevOps (User Settings > SSH public keys)
3. Add encrypted keys to chezmoi: `chezmoi add --encrypt ~/.ssh/id_ed25519_personal ~/.ssh/id_ed25519_personal.pub`
4. Update the public keys in `.chezmoidata/machines.yaml`

## Troubleshooting

**"error: Load key ... : No such file or directory"**: The key for your profile hasn't been deployed. Run `chezmoi apply` and check that your `machine_name` is set correctly in `~/.config/chezmoi/chezmoi.toml`.

**Agent doesn't have the key after reboot**: On macOS, keys should persist via Keychain. Re-run: `ssh-add --apple-use-keychain ~/.ssh/<keyfile>`. On Linux, add the `ssh-add` command to your shell profile.

**"signing key not found"**: The `signingkey` in `.chezmoidata/machines.yaml` doesn't match any key in `~/.ssh/`. Copy the correct public key and update the data file.

**GitHub shows "Unverified"**: Add your SSH signing key to GitHub (Settings > SSH and GPG keys > New SSH key > Key type: "Signing Key").

**ADO rejects your key**: Azure DevOps only accepts RSA keys. Make sure you're using `id_rsa_work`, not an Ed25519 key.
