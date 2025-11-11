---
name: conventional-commits
description: Create git commits following the Conventional Commits standard (v1.0.0) without AI attribution
---

# Conventional Commits Skill

This skill helps you create properly formatted git commits following the Conventional Commits specification.

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

**Primary types:**
- `feat`: A new feature (correlates with MINOR in SemVer)
- `fix`: A bug fix (correlates with PATCH in SemVer)

**Additional types:**
- `build`: Changes to build system or dependencies
- `chore`: Routine tasks, maintenance
- `ci`: Changes to CI configuration files and scripts
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, whitespace, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `revert`: Reverts a previous commit

## Breaking Changes

Indicate breaking changes with either:
- An exclamation mark after the type/scope:
  ```
  feat!: remove deprecated API
  ```
- A footer starting with BREAKING CHANGE:
  ```
  BREAKING CHANGE: description of the breaking change
  ```

Breaking changes correlate with MAJOR version bumps in SemVer.

## Rules

1. **NEVER mention AI, Claude, or automated generation** in commit messages
2. **Author must always be**: Michael Lee <michael@mrlee.io>
3. **DO NOT include** Co-Authored-By tags for AI/Claude
4. **DO NOT include** "Generated with Claude Code" or similar attributions
5. Keep the description concise and in imperative mood (e.g., "add" not "added")
6. Capitalize the description
7. No period at the end of the description
8. Body and footer are optional but recommended for complex changes

## Examples

### Simple feature
```
feat: Add user authentication module
```

### Bug fix with scope
```
fix(api): Correct null pointer in user lookup
```

### Breaking change
```
feat!: Remove support for Node 14

BREAKING CHANGE: Node 14 is no longer supported. Minimum version is now Node 18.
```

### With body
```
refactor: Simplify database connection logic

Consolidate connection pooling and error handling into
a single module for better maintainability.
```

## When to Use This Skill

Use this skill whenever you need to create a git commit. The skill ensures:
- Proper conventional commit formatting
- No AI attribution in commits
- Correct author information
- Professional, clean commit history

## Post-Commit Behavior

After creating a commit:
1. Confirm the commit was created successfully
2. Display only the commit message itself
3. **DO NOT** provide verbose explanations about the commit format
4. **DO NOT** break down the commit structure unless explicitly asked
5. Keep the response concise and to the point
