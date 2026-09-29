#!/usr/bin/env python3
"""Render/apply every supported profile in a temporary home, without installation scripts."""
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CHEZMOI = os.environ.get('CHEZMOI', 'chezmoi')

# Fail if provisioning hooks or encrypted credentials return to the source tree.
assert not any(p.is_file() for p in (ROOT / '.chezmoiscripts').rglob('*'))
assert not any(ROOT.rglob('encrypted_*.age'))


def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs).stdout


def validate_file(path, text):
    if path.endswith('.json'):
        json.loads(text)
    elif path.endswith('.toml'):
        tomllib.loads(text)
    elif path.endswith(('.plist', '.terminal')):
        plistlib.loads(text.encode())
    elif path.endswith('.sh'):
        run(['bash', '-n'], input=text)
    elif Path(path).name in ('dot_zshrc', 'dot_zshenv', 'dot_zprofile'):
        run(['zsh', '-n'], input=text)


with tempfile.TemporaryDirectory(prefix='dotfiles-test-') as scratch:
    scratch = Path(scratch)
    source = scratch / 'source'
    source.mkdir()
    # Copy configuration source only.
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if '.git' in relative.parts or '__pycache__' in relative.parts or not path.is_file():
            continue
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)

    for profile in ('personal', 'homelab', 'work'):
        for arch in ('arm64', 'amd64'):
            case = scratch / f'{profile}-{arch}'
            case.mkdir()
            destination = case / 'home'
            destination.mkdir()
            # App-owned state and overrides must survive a normal apply unchanged.
            local_files = {
                '.gitconfig.local': '[user]\n  name = Local Override\n',
                '.config/ghostty/config.local': 'font-size = 17\n',
                '.config/gh/hosts.yml': 'test-auth-state\n',
                '.ssh/id_ed25519_personal': 'test-key-state\n',
                'Library/Application Support/Code/User/settings.json': '{"editor.tabSize": 8}\n',
            }
            for name, content in local_files.items():
                path = destination / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            config = case / 'config.toml'
            config.write_text(f'[data]\nmachine_name = "{profile}"\n')
            base = [CHEZMOI, '--config', str(config), '--source', str(source),
                    '--destination', str(destination), '--cache', str(case / 'cache'),
                    '--persistent-state', str(case / 'state.boltdb'),
                    '--override-data', json.dumps({'chezmoi': {'os': 'darwin', 'arch': arch}})]
            for path in sorted(source.rglob('*')):
                if not path.is_file() or '.chezmoitemplates' in path.parts:
                    continue
                text = path.read_text()
                relative = str(path.relative_to(source))
                if path.suffix == '.tmpl':
                    args = base + ['execute-template', '--file', str(path)]
                    if path.name == '.chezmoi.toml.tmpl':
                        args.append('--init')
                    text = run(args)
                    relative = relative.removesuffix('.tmpl')
                validate_file(relative, text)
            # No apply hooks remain: exercise a normal configuration apply.
            run(base + ['apply', '--force'])
            for name, content in local_files.items():
                assert (destination / name).read_text() == content
            env = dict(os.environ, HOME=str(destination))
            assert run(['git', 'config', '--file', str(destination / '.gitconfig'),
                        '--includes', '--get', 'user.name'], env=env).strip() == 'Local Override'
            atuin = tomllib.loads((destination / '.config/atuin/config.toml').read_text())
            assert atuin['auto_sync'] is False and atuin['update_check'] is False
            assert atuin['sync_address'] == 'http://127.0.0.1:1'
            # Parse the rendered SSH configuration with OpenSSH itself.
            ssh_config = run(['ssh', '-G', '-F', str(destination / '.ssh/config'), 'github.com'])
            assert 'com.1password/t/agent.sock' in ssh_config
            assert 'identityfile ~/.ssh/github.pub' in ssh_config
            assert 'identitiesonly yes' in ssh_config
            assert 'user git\n' in ssh_config
            public_key = (destination / '.ssh/github.pub').read_text().strip()
            signing_key = run(['git', 'config', '--file', str(destination / '.gitconfig'),
                               '--get', 'user.signingkey']).strip()
            assert public_key == signing_key
            if profile == 'work':
                assert signing_key.startswith('ssh-rsa ')
                azure_config = run(['ssh', '-G', '-F', str(destination / '.ssh/config'),
                                    'ssh.dev.azure.com'])
                assert 'com.1password/t/agent.sock' in azure_config
                assert 'identityfile ~/.ssh/github.pub' in azure_config
                assert 'identitiesonly yes' in azure_config
                assert 'identityfile ~/.ssh/id_rsa_work' not in azure_config
            assert not (destination / 'Library/LaunchAgents/com.atuin.server.plist').exists()
            assert not (destination / 'tests').exists()
            assert not (destination / 'Brewfile').exists()
            assert not (destination / 'dependencies.json').exists()
            # Applying again must produce no file drift.
            assert not run(base + ['diff']).strip()
            print(f'PASS {profile}/{arch}: render, syntax, idempotence')

    invalid = subprocess.run(base + ['--override-data', '{"machine_name":"invalid"}',
                                    'execute-template', '--init', '--file',
                                    str(source / '.chezmoi.toml.tmpl')], text=True, capture_output=True)
    assert invalid.returncode != 0 and 'machine_name must be' in invalid.stderr
    print('PASS invalid profile rejected')

# Non-template custom functions must also parse without running user startup files.
for path in (ROOT / 'dot_zsh/functions').iterdir():
    run(['zsh', '-n', str(path)])
print('All configuration checks passed')
