# Codex policy

For fresh macOS machines with Codex CLI 0.154.0 or newer. The policy was validated
with 0.154.0; permission profiles and command rules are still evolving features.
The optional Brewfile includes Codex. Software installation remains separate
from chezmoi apply.

## Source files

- `.chezmoitemplates/agent-instructions.md`: the single source for global workflow
  preferences, signing behavior, and the inline Conventional Commits reference.
- `dot_codex/AGENTS.md.tmpl`: renders that text to `~/.codex/AGENTS.md`.
  Claude's `CLAUDE.md.tmpl` renders the same text without a runtime dependency
  on the other application.
- `dot_codex/config.toml.tmpl`: renders `~/.codex/config.toml`. It reuses protected
  paths, known secret variable names, and development hosts from
  `.chezmoitemplates/claude-settings/common.json`, then adds Codex-specific policy.
- `dot_codex/rules/safety.rules`: supplemental command denials. User-created
  `default.rules`, authentication, sessions, and other app state stay unmanaged.

## Behavior

The `development` permission profile extends `:workspace`. Normal file reads,
workspace edits, temporary files, and commands remain available. Sensitive
paths are read-only or denied entirely; `.env` files and `secrets` directories
are unreadable, including `.env.example`. Codex's auth file is denied, and its
global configuration directory and workspace policy directories are read-only.
The sandbox fails when it cannot enforce the selected restrictions.

AWS files (`~/.aws`), GitHub CLI configuration (`~/.config/gh`), and macOS
Keychains are readable but remain protected against writes. This permits file
reads needed for authentication; it does not guarantee access through Keychain
services or permit credential refreshes that need to write cached state.

Workspace Git metadata (`.git`) is explicitly writable so staging and commits
can create lock files, update the index, and write objects and refs. Git config
and hooks remain read-only. Worktrees with Git metadata outside the workspace
may still need a reviewed permission exception for their actual Git directory.

Sandbox escalation, additional permission requests, and command-rule approval
requests are eligible for automatic review instead of being rejected outright.
An approval can still be denied; it cannot override an outer OS sandbox or
administrator policy. Skill-script approvals remain disabled and MCP elicitation
prompts remain interactive. There are no shipped command `allow` rules that
authorize unsandboxed execution. GitHub and AWS authentication variables are inherited.
Automatic KEY/SECRET/TOKEN name exclusions are disabled because they also remove
those credentials; the explicit list still excludes OpenAI, Anthropic, and npm
credentials. Other unlisted secrets in the parent environment can be inherited.
Login-shell execution is disabled. Inherit the required tool PATH before launching Codex.
Shell scripts can still load additional environment values; these filters are
not a guarantee that every possible credential is unavailable.

The network proxy is explicitly enabled so command traffic uses the shared
development-host allowlist. HTTP methods are unrestricted on allowed hosts.
Unlisted hosts, private-network access, and arbitrary Unix sockets are not
pre-approved. Local service access needs a deliberate, narrow host exception.
Codex's `allow_local_binding` has broader private-network implications than
Claude's similarly named setting, so it stays off. Hosted web search is enabled
and uses a separate access path.

The shared allowlist includes AWS API, sign-in, and SSO hosts under
`*.amazonaws.com`, `*.aws.amazon.com`, and `*.awsapps.com`. These host rules allow
all accounts and API operations authorized by the available credentials.
`AWS_EC2_METADATA_DISABLED=true` prevents instance-metadata credential fallback on
these macOS profiles. Choose a configured profile with `AWS_PROFILE` or `--profile`;
this setting does not supply credentials or select an AWS account.

Other credential-dependent tools, private package downloads, SSH signing, Docker,
global installations, and some skills may be blocked. Run blocked administration
or credential-dependent operations yourself. Add only narrowly scoped cache or
host access when needed; avoid blanket sandbox bypasses.

## Limits and overrides

Command rules match literal argument prefixes. They catch listed invocations,
including this repo's `git pf` alias, but do not classify equivalent behavior in
scripts, arbitrary aliases, reordered options, or direct API calls. For example,
`git push --force origin main` matches while `git push origin main --force` does
not. The OS sandbox is the primary boundary; it still permits destructive
changes within writable projects. Keep recoverable work and backups.

These are user defaults, not administrator-enforced policy. Higher-precedence
configuration, runtime permission selection, additional allow rules, and
explicit CLI overrides can change them. Do not combine permission profiles with
legacy `sandbox_mode` or `sandbox_workspace_write` settings: legacy settings can
take precedence. The desktop app may supply its own task permissions; verify the
effective profile there rather than assuming this file locks every surface.

The command network policy does not govern web search, browser/computer use,
MCP servers, connectors, or Codex's own model/authentication traffic. Those
surfaces need their own controls. Allowed hosts can still receive data or
mutations if a process has suitable credentials. An `AGENTS.override.md` in
Codex's home can replace the shared global instructions.

## Validate and apply

Run the repository's normal profile checks:

```sh
CHEZMOI=chezmoi python3 tests/validate.py
```

With Codex installed, run the native policy tests from a normal macOS terminal:

```sh
CHEZMOI=chezmoi CODEX=codex python3 tests/validate_codex.py --network
```

They use synthetic temporary files and inspect command decisions without
executing destructive commands. The optional network check sends unauthenticated
HEAD requests to GitHub (allowed) and example.com (denied). An outer sandbox can
prevent this test from starting its own local proxy. The tests do not apply the
configuration to your real home directory.

After reviewing the diff, apply the managed files and restart Codex:

```sh
chezmoi diff ~/.claude/CLAUDE.md ~/.codex
chezmoi apply ~/.claude/CLAUDE.md ~/.codex
```

Use `/permissions` to confirm the active profile and `codex --strict-config
doctor --summary` to inspect configuration diagnostics. Model, authentication,
and application preferences are not selected by this template. Chezmoi owns the
deployed config file; persistent changes to managed settings belong in its source.
Applying only source edits does not update an already-running task's permissions.
Restart the application and create a fresh task after applying. Before overwriting
the live Codex config, preserve app-added plugin, MCP, notification, and project
settings that are not represented in the template.

References:

- [Global instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Permission profiles](https://learn.chatgpt.com/docs/permissions)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Command rules](https://learn.chatgpt.com/docs/agent-configuration/rules)
