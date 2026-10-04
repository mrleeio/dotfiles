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

    for profile in ('personal', 'work'):
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
            # Ctrl-R searches the repository, falling back to the directory outside one.
            assert 'filter_mode' not in atuin
            assert atuin['search']['filters'] == ['workspace', 'directory']
            # Parse the rendered SSH configuration with OpenSSH itself.
            for host in ('github.com', 'ssh.dev.azure.com'):
                ssh_config = run(['ssh', '-G', '-F', str(destination / '.ssh/config'), host])
                assert 'com.1password/t/agent.sock' in ssh_config
                assert 'identitiesonly no' in ssh_config
            assert 'loglevel ERROR' in ssh_config
            assert not (destination / '.ssh/github.pub').exists()
            signing_key = run(['git', 'config', '--file', str(destination / '.gitconfig'),
                               '--get', 'user.signingkey']).strip()
            agent = tomllib.loads((destination / '.config/1Password/ssh/agent.toml').read_text())
            items = [key['item'] for key in agent['ssh-keys']]
            if profile == 'work':
                assert items == ['Gen 2 Fund SSH Key', 'Michael Lee SSH Key']
                assert signing_key.startswith('ssh-rsa ')
            else:
                assert items == ['Michael Lee SSH Key', 'Gen 2 Fund SSH Key']
            # macOS path_helper (/etc/zprofile) must not demote Homebrew or mise in login shells.
            brew_bin = '/opt/homebrew/bin' if arch == 'arm64' else '/usr/local/bin'
            shims = str(destination / '.local/share/mise/shims')
            for login in ([], ['-l']):
                path = run(['env', '-i', f'HOME={destination}', 'zsh', *login, '-c',
                            'print -r -- $PATH']).strip().split(':')
                assert path.index(shims) < path.index('/usr/bin'), path
                if os.access(f'{brew_bin}/brew', os.X_OK):
                    assert path.index(brew_bin) < path.index('/usr/bin'), path
            # Interactive startup caches and compiles the completion dump under XDG_CACHE_HOME.
            for _ in range(2):
                subprocess.run(['env', '-i', f'HOME={destination}', 'TERM=dumb', 'zsh', '-i', '-c',
                                'exit'], check=True, capture_output=True, stdin=subprocess.DEVNULL)
            dumps = list((destination / '.cache/zsh').glob('zcompdump-*'))
            assert sorted(p.name.endswith('.zwc') for p in dumps) == [False, True], dumps
            assert not list(destination.glob('.zcompdump*'))
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

RUBY_LSP_CHECK = """
local config_path, project, record = _G.arg[1], _G.arg[2], _G.arg[3]
local config = dofile(config_path)
config.filetypes = { 'ruby' }
vim.lsp.config('ruby_lsp', config)
vim.lsp.enable('ruby_lsp')
local function open()
  vim.cmd('silent! %bwipeout!')
  vim.cmd.edit(project .. '/lib/app.rb')
  vim.bo.filetype = 'ruby'
end
-- Headless confirm() declines the trust prompt.
open()
vim.wait(500)
assert(not vim.uv.fs_stat(record), 'Ruby LSP started in an untrusted project')
vim.secure.trust({ action = 'allow', path = project })
open()
assert(vim.wait(5000, function() return vim.uv.fs_stat(record) ~= nil end),
  'Ruby LSP did not start in a trusted project')
"""

with tempfile.TemporaryDirectory(prefix='dotfiles-ruby-lsp-') as scratch:
    scratch = Path(scratch)
    project = scratch / 'project'
    (project / 'lib').mkdir(parents=True)
    (project / 'Gemfile').write_text("raise 'Gemfile evaluated'\n")
    (project / 'lib/app.rb').write_text('')
    bin_dir = scratch / 'bin'
    bin_dir.mkdir()
    record = scratch / 'mise-call'
    (bin_dir / 'mise').write_text(f'#!/bin/sh\nprintf "%s\\n" "$PWD" "$@" > "{record}"\n')
    (bin_dir / 'mise').chmod(0o755)
    (scratch / 'check.lua').write_text(RUBY_LSP_CHECK)
    env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}",
               XDG_STATE_HOME=str(scratch / 'state'))
    run(['nvim', '--headless', '--clean', '-l', str(scratch / 'check.lua'),
         str(ROOT / 'dot_config/exact_nvim/after/lsp/ruby_lsp.lua'), str(project), str(record)],
        env=env, stdin=subprocess.DEVNULL)
    # mise selects the project's Ruby from the project root, not Homebrew's.
    cwd, *args = record.read_text().splitlines()
    assert Path(cwd).resolve() == project.resolve() and args == ['exec', '--', 'ruby-lsp']
print('PASS Ruby LSP requires trust and runs through mise')

with tempfile.TemporaryDirectory(prefix='dotfiles-vim-up-') as scratch:
    scratch = Path(scratch)
    upstream = scratch / 'upstream'
    run(['git', 'init', '-q', str(upstream)])
    (upstream / 'plugin.zsh').write_text('# plugin\n')
    run(['git', '-C', str(upstream), 'add', '.'])
    run(['git', '-C', str(upstream), '-c', 'user.name=Test', '-c', 'user.email=test@example.com',
         '-c', 'commit.gpgsign=false', 'commit', '-qm', 'init'])
    revision = run(['git', '-C', str(upstream), 'rev-parse', 'HEAD']).strip()
    source = scratch / 'source'
    bin_dir = scratch / 'bin'
    source.mkdir()
    bin_dir.mkdir()
    for name, body in {'chezmoi': f'echo "{source}"', 'nvim': 'exit 0'}.items():
        (bin_dir / name).write_text(f'#!/bin/sh\n{body}\n')
        (bin_dir / name).chmod(0o755)
    env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}")
    destination = scratch / 'plugins/example'

    def vim_up(rev):
        (source / 'dependencies.json').write_text(json.dumps(
            [{'repository': str(upstream), 'revision': rev, 'directory': str(destination)}]))
        return subprocess.run(['zsh', '-fc', f'fpath=({ROOT / "dot_zsh/functions"}); '
                               'autoload -Uz vim-up; vim-up'],
                              env=env, text=True, capture_output=True)

    # A failed checkout leaves nothing behind, so a retry installs it.
    assert vim_up('0' * 40).returncode != 0
    assert not destination.exists() and not list(destination.parent.glob('.vim-up-*'))
    assert vim_up(revision).returncode == 0 and (destination / 'plugin.zsh').exists()
    # A clone interrupted before checkout is completed, not kept as installed.
    shutil.rmtree(destination)
    run(['git', 'clone', '-q', '--no-checkout', str(upstream), str(destination)])
    assert vim_up(revision).returncode == 0 and (destination / 'plugin.zsh').exists()
    # Anything else at the destination fails instead of reporting success.
    shutil.rmtree(destination)
    destination.mkdir()
    assert vim_up(revision).returncode != 0
print('PASS vim-up recovers from interrupted installs')

# whats-in-port and clear-port find and stop every listener on a port.
server = subprocess.Popen(['python3', '-c', 'import socket, time; s = socket.socket(); '
                           's.bind(("127.0.0.1", 0)); s.listen(); print(s.getsockname()[1], '
                           'flush=True); time.sleep(60)'], stdout=subprocess.PIPE, text=True)
try:
    port = server.stdout.readline().strip()
    functions = f'fpath=({ROOT / "dot_zsh/functions"}); autoload -Uz whats-in-port clear-port; '
    assert str(server.pid) in run(['zsh', '-fc', functions + f'whats-in-port {port}'])
    run(['zsh', '-fc', functions + f'clear-port {port}'])
    assert server.wait(timeout=10) != 0
    assert subprocess.run(['zsh', '-fc', functions + f'clear-port {port}'],
                          capture_output=True).returncode != 0
finally:
    server.kill()
print('PASS port helpers find and stop listeners')

# Non-template custom functions must also parse without running user startup files.
for path in (ROOT / 'dot_zsh/functions').iterdir():
    run(['zsh', '-n', str(path)])
print('All configuration checks passed')
