# Workflow

- Complete clearly requested, reversible work without asking for approval at each step. Ask when ambiguity materially changes the outcome or an action exceeds the requested scope.
- When sandbox or permission restrictions block an operation, do not weaken settings or attempt an equivalent bypass. Continue independent work and report the blocked operation.
- Summarize what changed, what you verified, and any remaining blockers. Distinguish implemented changes from changes actually deployed or applied.
- Run checks appropriate to the change. For bug fixes, prefer a regression test that reproduces the failure. Report checks you could not run.

# Git

- If commit signing fails, report the failure rather than disabling signing or creating an unsigned commit.
- Use Conventional Commits 1.0.0 for commit messages in all projects, following the reference below.

## Conventional Commits

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

- Use `feat` for a new feature and `fix` for a bug fix. Other common types are `docs` (documentation), `refactor` (restructuring without a feature or fix), `perf` (performance), `test` (tests), `build` (build tooling or dependencies), `ci` (automation), `style` (formatting), `chore` (maintenance), and `revert` (undoing a change). Follow the repository's type conventions where applicable.
- An optional scope names the affected component in parentheses, such as `fix(auth): handle expired sessions`.
- Write a short description after the required colon and space. Prefer lowercase types and imperative descriptions, such as `add`, `fix`, or `remove`.
- Use an optional body to explain motivation and relevant consequences. Separate it from the subject with a blank line.
- Mark a breaking change with `!` immediately before the colon, or an uppercase `BREAKING CHANGE: <explanation>` footer. Either marker is sufficient; explain what breaks and how to migrate in the description or body when using only `!`. Any type can carry a breaking change.
- Separate footers from the preceding content with a blank line. Use trailers such as `Refs: #123` or `Reviewed-by: Name`; retain required signing and attribution conventions. For a revert, identify the reverted commit in the body or a `Refs:` footer.
- Keep commits focused. Separate unrelated changes when practical rather than combining multiple purposes under one subject.

Examples:

```text
feat(search): add filtering by file type
fix(auth): reject expired refresh tokens
docs: clarify first-time setup
refactor!: remove the deprecated configuration loader

Read configuration through loadConfig() instead of loadLegacyConfig().

BREAKING CHANGE: loadLegacyConfig() is no longer exported.
```
