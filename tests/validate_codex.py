#!/usr/bin/env python3
"""Exercise Codex's actual rule engine and macOS sandbox with synthetic files.

Requires Python 3.11+, chezmoi, and Codex 0.154.0+. Run from a normal terminal:
an outer agent sandbox may prevent the nested sandbox proxy from starting.
Pass --network to additionally check two public hosts; no authentication is used.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CODEX = os.environ.get('CODEX', 'codex')
CHEZMOI = os.environ.get('CHEZMOI', 'chezmoi')


def inline_toml(value):
    """Encode CLI overrides without shell interpolation."""
    if isinstance(value, dict):
        return '{' + ', '.join(json.dumps(k) + ' = ' + inline_toml(v)
                               for k, v in value.items()) + '}'
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, list):
        return '[' + ', '.join(map(inline_toml, value)) + ']'
    return json.dumps(value)


def run(args):
    return subprocess.run(args, capture_output=True, text=True, timeout=45)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--network', action='store_true')
    options = parser.parse_args()
    rules = ROOT / 'dot_codex/rules/safety.rules'
    cases = [
        (['sudo', 'true'], 'forbidden'),
        (['git', 'reset', '--hard', 'HEAD'], 'forbidden'),
        (['git', 'clean', '-dfx'], 'forbidden'),
        (['git', 'push', '--force', 'origin', 'main'], 'forbidden'),
        (['git', 'pf', 'origin', 'main'], 'forbidden'),
        (['gh', 'repo', 'delete', 'owner/repo', '--yes'], 'forbidden'),
        (['rm', '-rf', '/'], 'forbidden'),
        (['git', 'status'], None),
        (['git', 'clean', '-nd'], None),
        (['git', 'push', 'origin', 'feature'], None),
        (['rm', '-rf', 'build'], None),
    ]
    for command, expected in cases:
        result = run([CODEX, 'execpolicy', 'check', '--rules', str(rules), '--', *command])
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout).get('decision') == expected, result.stdout
    print('PASS native command rules and inline rule examples')

    with tempfile.TemporaryDirectory(prefix='codex-policy-test-') as scratch:
        scratch = Path(scratch).resolve()
        chezmoi_config = scratch / 'chezmoi.toml'
        chezmoi_config.write_text('[data]\nmachine_name = "personal"\n')
        rendered = run([CHEZMOI, '--config', str(chezmoi_config), '--source', str(ROOT),
                        'execute-template', '--file', str(ROOT / 'dot_codex/config.toml.tmpl')])
        assert rendered.returncode == 0, rendered.stderr
        config = tomllib.loads(rendered.stdout)
        workspace = scratch / 'workspace'
        workspace.mkdir()
        initialized = run(['git', 'init', str(workspace)])
        assert initialized.returncode == 0, initialized.stderr
        (workspace / 'nested').mkdir()
        (workspace / 'nested/.env').write_text('FAKE_SECRET=fixture')
        (workspace / 'secrets').mkdir()
        (workspace / 'secrets/fixture.txt').write_text('fake fixture')
        (workspace / '.codex').mkdir()
        (workspace / '.codex/config.toml').write_text('')
        readonly = scratch / 'readonly'
        readonly.mkdir()
        # An explicit read-only fixture tests writes without touching real home files.
        config['permissions']['development']['filesystem'][str(readonly)] = 'read'
        args = [CODEX]
        for key, value in config.items():
            args += ['-c', key + '=' + inline_toml(value)]
        args += ['sandbox', '-P', 'development', '-C', str(workspace), '--']
        script = '''from pathlib import Path
import subprocess
Path('allowed.txt').write_text('ok')
assert Path('allowed.txt').read_text() == 'ok'
subprocess.run(['git', 'add', 'allowed.txt'], check=True)
staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], text=True)
assert staged.strip() == 'allowed.txt', staged
for name in ['nested/.env', 'secrets/fixture.txt']:
    try: Path(name).read_text()
    except PermissionError: pass
    else: raise AssertionError('unexpected read: ' + name)
for name in ['.codex/config.toml', '.git/config', '.git/hooks/test-hook', %r]:
    try: Path(name).write_text('should fail')
    except PermissionError: pass
    else: raise AssertionError('unexpected write: ' + name)
''' % str(readonly / 'new.txt')
        result = run(args + ['/usr/bin/python3', '-c', script])
        assert result.returncode == 0, result.stdout + result.stderr
        print('PASS native sandbox: Git staging, workspace edits, secret reads, policy writes, read-only paths')
        if options.network:
            for host, allowed in [('github.com', True), ('example.com', False)]:
                result = run(args + ['/usr/bin/curl', '-sS', '-I', '--fail', '--max-time',
                                     '15', 'https://' + host])
                if allowed:
                    assert result.returncode == 0, result.stdout + result.stderr
                else:
                    assert result.returncode == 22, result.stdout + result.stderr
                    assert 'blocked-by-allowlist' in result.stdout.lower(), result.stdout
            print('PASS network proxy: allowed host reachable, unlisted host explicitly denied')


if __name__ == '__main__':
    main()
