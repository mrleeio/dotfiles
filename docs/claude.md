# Claude Code policy

The source is `.chezmoitemplates/claude-settings/common.json`.
`dot_claude/settings.json.tmpl` adds the selected machine's commit attribution
and renders `~/.claude/settings.json`. All three profiles share the policy.

`.chezmoitemplates/agent-instructions.md` holds the shared global instructions.
`dot_claude/CLAUDE.md.tmpl` and `dot_codex/AGENTS.md.tmpl` deploy identical text
for Claude and Codex. The instructions cover:
autonomy within the requested scope, respect for security boundaries, concise
completion reports, proportionate verification, preserved commit signing, and
Conventional Commits. Claude Code chooses its search tools using its built-in
behavior.

See [Codex policy](codex.md) for its permission profile and command rules.

Reviewed on 2026-09-14 against the official settings reference and published
Claude Code changelog (latest listed release: **2.1.272**). The locally installed
CLI was subsequently verified at **2.1.270** after a Homebrew upgrade. No settings
migration is needed for that upgrade. Releases 2.1.271 and 2.1.272 include further
permission-check and reliability fixes; install them through Homebrew when
available. This repository does not pin or upgrade the CLI.

## Routine work

- `acceptEdits` approves file edits in working directories. Sandboxed Bash
  commands are auto-approved, so a command-by-command Bash allowlist is unnecessary.
- File reads under `~/GitHub`, web fetches, and web searches are pre-approved.
  Explicit deny rules still take precedence.
- Downloads with `curl` and `wget` work through the sandbox network allowlist.
  Unlisted hosts require approval. The bare `WebFetch` tool permission does not
  grant arbitrary sandbox network access; `WebFetch(domain:*)` would.
- Development servers can bind locally. Unix sockets and Apple Events remain
  restricted; Docker and macOS automation may consequently be unavailable.
- No extra home-directory write access is granted. If a package manager needs a
  cache outside the project, grant only that specific cache in project-local
  `sandbox.filesystem.allowWrite`, or configure a project-local cache.

## Boundaries

- The sandbox must initialize or Claude Code exits. Unsandboxed retries and
  command exclusions are disabled. Filesystem isolation stays enabled, with
  neither weaker network nor weaker nested-sandbox isolation enabled.
- Most credential directories, credential files, `.env`/`.env.*` files, and `secrets`
  directories are denied reads through both the sandbox and built-in file tools.
  These patterns also block `.env.example` and `.env.test`; use a differently
  named, sanitized fixture when needed. An allow rule cannot override a deny.
- AWS files (`~/.aws`), GitHub CLI configuration (`~/.config/gh/hosts.yml`), and
  macOS Keychains permit reads while remaining protected against writes.
  Keychain service access and authentication cache refreshes may still fail.
- GitHub and AWS authentication environment variables are permitted. Known
  OpenAI, Anthropic, and npm credential variables are removed from sandboxed commands.
  This complements file protection; it is an explicit list, not a detector for
  every possible secret variable.
- System paths, credential storage, installed Homebrew software, global shell
  startup files, Git configuration, and the deployed Claude policy are protected
  from writes. The chezmoi source remains editable for reviewed changes.
- Command deny rules block common invocations of privilege escalation, disk
  destruction, shutdown, hard resets, forced Git cleanup and pushes, and GitHub
  repository deletion. Normal sandboxed development commands remain available.

SSH Git operations/signing and private package downloads can still fail because
other credentials remain hidden. AWS API, sign-in, and SSO hosts are permitted
under `*.amazonaws.com`, `*.aws.amazon.com`, and `*.awsapps.com`.
`AWS_EC2_METADATA_DISABLED=true` disables EC2 metadata fallback on these Macs;
select a configured AWS profile with `AWS_PROFILE` or `--profile`.
Authentication cache writes and custom identity-provider hosts may still need
specific permissions. Apply the configuration and restart the agent to load changes.
Run credential-dependent operations in your own terminal, or deliberately revise
the policy for a narrowly scoped credential. Do not add blanket command exclusions
or home-directory write access to fix these failures.

## Limits

This is a permissive development policy, not a guarantee against all destructive
behavior. Bash patterns match command text: alternate option placement, wrappers,
scripts, and direct API calls can perform equivalent operations without matching
the listed commands. The sandbox still permits arbitrary changes inside writable
projects. Keep backups and use disposable worktrees for untrusted work.

The network allowlist controls hosts, not HTTP methods or repository ownership.
An allowed host such as GitHub can receive data and mutations if a command has
credentials. WebFetch and MCP tools run outside the Bash sandbox; MCP permissions
still require their own review. Hostname filtering is not a complete network
data-loss-prevention mechanism.

These are user settings. Higher-precedence settings can change Boolean values,
and arrays merge across scopes, including command exclusions and allowed domains.
Check the effective configuration in each project. Managed settings or an outer
container/VM are needed for stronger enforcement. On Linux, wildcard write rules
are not enforced by the sandbox; these dotfiles target macOS. Concrete protected
directory paths are used wherever possible.

## Apply and verify

Run `chezmoi diff ~/.claude/settings.json ~/.claude/CLAUDE.md`, then
`chezmoi apply ~/.claude/settings.json ~/.claude/CLAUDE.md` when ready to deploy
the policy and global instructions. In a new
Claude Code session, use `/status`, `/permissions`, and `/sandbox` to confirm the
loaded sources, deny rules, and sandbox restrictions; run `claude doctor` for
configuration warnings. Repository validation renders and applies every profile
and architecture in temporary homes, preserving machine-specific attribution.

References:

- [Settings reference](https://code.claude.com/docs/en/settings-reference)
- [Current search tool behavior](https://code.claude.com/docs/en/tools-reference#glob-tool-behavior)
- [Permission semantics and pattern limitations](https://code.claude.com/docs/en/permissions)
- [Sandbox behavior and limitations](https://code.claude.com/docs/en/sandboxing)
- [Settings precedence](https://code.claude.com/docs/en/settings)
- [Official changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
