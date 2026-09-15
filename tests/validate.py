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
                '.codex/auth.json': '{"test": "auth-state"}\n',
                '.codex/rules/default.rules': '# User-owned approvals\n',
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
                azure_config = run(['ssh', '-G', '-F', str(destination / '.ssh/config'),
                                    'ssh.dev.azure.com'])
                assert 'identitiesonly no' in azure_config
                assert 'identityfile ~/.ssh/id_rsa_work' not in azure_config
            assert not (destination / 'Library/LaunchAgents/com.atuin.server.plist').exists()
            assert not (destination / 'tests').exists()
            assert not (destination / 'Brewfile').exists()
            assert not (destination / 'dependencies.json').exists()
            settings = json.loads((destination / '.claude/settings.json').read_text())
            email = 'mlee@gen2fund.com' if profile == 'work' else 'michael@mrlee.io'
            assert settings['attribution']['commit'] == f'Authored-By: Michael Lee <{email}>'
            assert settings['sandbox']['excludedCommands'] == []
            assert settings['sandbox']['network']['allowAllUnixSockets'] is False
            # Both agents must receive the exact shared instructions, not an import
            # or a symlink that relies on the other application being installed.
            instructions = (source / '.chezmoitemplates/agent-instructions.md').read_bytes()
            assert (destination / '.claude/CLAUDE.md').read_bytes() == instructions
            assert (destination / '.codex/AGENTS.md').read_bytes() == instructions
            codex = tomllib.loads((destination / '.codex/config.toml').read_text())
            assert 'sandbox_mode' not in codex and 'sandbox_workspace_write' not in codex
            policy = codex['permissions'][codex['default_permissions']]
            assert policy['extends'] == ':workspace'
            assert codex['features']['network_proxy'] is True
            assert policy['network']['enabled'] is True
            assert set(policy['network']['domains']) == set(settings['sandbox']['network']['allowedDomains'])
            for path in settings['sandbox']['filesystem']['denyRead']:
                assert policy['filesystem'][path] == 'deny'
            assert policy['filesystem']['~/.codex/auth.json'] == 'deny'
            assert policy['filesystem']['~/.codex'] == 'read'
            for path, read_rule in (
                ('~/.aws', 'Read(~/.aws/**)'),
                ('~/.config/gh', 'Read(~/.config/gh/hosts.yml)'),
                ('~/Library/Keychains', 'Read(~/Library/Keychains/**)'),
            ):
                assert policy['filesystem'][path] == 'read'
                assert path in settings['sandbox']['filesystem']['denyWrite']
                assert path not in settings['sandbox']['filesystem']['denyRead']
                assert read_rule not in settings['permissions']['deny']
            assert '~/.config/gh/hosts.yml' not in settings['sandbox']['filesystem']['denyRead']
            assert policy['filesystem'].get('~/.config/gh/hosts.yml', 'read') == 'read'
            auth_variables = {'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN',
                              'GH_TOKEN', 'GITHUB_TOKEN', 'GH_ENTERPRISE_TOKEN', 'GITHUB_ENTERPRISE_TOKEN'}
            denied_variables = {entry['name'] for entry in settings['sandbox']['credentials']['envVars']}
            assert auth_variables.isdisjoint(denied_variables)
            shell_policy = codex['shell_environment_policy']
            assert shell_policy['inherit'] == 'all'
            assert shell_policy['ignore_default_excludes'] is True
            assert auth_variables.isdisjoint(shell_policy['filters'])
            assert shell_policy['filters']['OPENAI_API_KEY'] == 'exclude'
            assert shell_policy['set']['AWS_EC2_METADATA_DISABLED'] == 'true'
            assert settings['env']['AWS_EC2_METADATA_DISABLED'] == 'true'
            for host in ('*.amazonaws.com', '*.aws.amazon.com', '*.awsapps.com'):
                assert policy['network']['domains'][host] == 'allow'
            assert policy['network']['allow_local_binding'] is False
            assert codex['approvals_reviewer'] == 'auto_review'
            for category in ('sandbox_approval', 'request_permissions', 'rules'):
                assert codex['approval_policy']['granular'][category] is True
            assert codex['approval_policy']['granular']['skill_approval'] is False
            workspace_policy = policy['filesystem'][':workspace_roots']
            assert workspace_policy['.git'] == 'write'
            assert workspace_policy['.git/config'] == 'read'
            assert workspace_policy['.git/hooks'] == 'read'
            # Applying again must produce no file drift.
            assert not run(base + ['diff']).strip()
            print(f'PASS {profile}/{arch}: render, syntax, policy, permissions, idempotence')

    invalid = subprocess.run(base + ['--override-data', '{"machine_name":"invalid"}',
                                    'execute-template', '--init', '--file',
                                    str(source / '.chezmoi.toml.tmpl')], text=True, capture_output=True)
    assert invalid.returncode != 0 and 'machine_name must be' in invalid.stderr
    print('PASS invalid profile rejected')

# Non-template custom functions must also parse without running user startup files.
for path in (ROOT / 'dot_zsh/functions').iterdir():
    run(['zsh', '-n', str(path)])
print('All configuration checks passed')
