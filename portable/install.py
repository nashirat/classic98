#!/usr/bin/env python3
"""Portable, user-local Classic 98 installation and theme-switch hooks."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
CONFIG = HOME / '.config'
DATA = HOME / '.local/share/classic98'
STATE = HOME / '.local/state/classic98-installer'
PIN = 'efb50993780079460b0cbed1363e2166a2de1d9f'
CURSOR = 'Classic98'


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def save_json(path, value):
    write_text(path, json.dumps(value, indent=2) + '\n')


def write_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Preserve a linked config's original target; the backup retains the link.
    if path.is_symlink():
        path.unlink()
    path.write_text(value)


def snapshot(paths, directory):
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    for i, path in enumerate(paths):
        exists = path.exists() or path.is_symlink()
        records.append({'path': str(path), 'exists': exists})
        if exists:
            if path.is_dir() and not path.is_symlink():
                shutil.copytree(path, directory / str(i), symlinks=True)
            else:
                shutil.copy2(path, directory / str(i), follow_symlinks=False)
    save_json(directory / 'manifest.json', records)


def restore(directory):
    for i, record in enumerate(json.loads((directory / 'manifest.json').read_text())):
        path = Path(record['path'])
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
        if record['exists']:
            path.parent.mkdir(parents=True, exist_ok=True)
            source = directory / str(i)
            if source.is_dir() and not source.is_symlink():
                shutil.copytree(source, path, symlinks=True)
            else:
                shutil.copy2(source, path, follow_symlinks=False)


def shell_paths():
    return [CONFIG / 'omarchy/shell.json', CONFIG / 'omarchy/shell.toml']


def theme_name():
    return (HOME / '.local/state/omarchy/current/theme.name').read_text().strip()


def apply_shell():
    base = json.loads(shell_paths()[0].read_text()) if shell_paths()[0].exists() else {'version': 1}
    layout = json.loads((DATA / 'layout.json').read_text())
    base['bar'] = layout['bar']
    base['disabledPlugins'] = list(dict.fromkeys(base.get('disabledPlugins', []) + ['omarchy.menu', 'omarchy.osd']))
    base['plugins'] = [p for p in base.get('plugins', []) if p.get('id') not in ('omarchy.osd', 'nash.osd')]
    base['plugins'].append({'id': 'nash.osd'})
    base['cloneSourceRestores'] = list(dict.fromkeys(base.get('cloneSourceRestores', []) + ['nash.menu', 'nash.osd']))
    save_json(shell_paths()[0], base)
    write_text(shell_paths()[1], '[font]\nbase-size = 12\n')


def decorations(theme):
    plugin = DATA / 'native-titlebar/hyprbars/hyprbars.so'
    loaded = 'Plugin hyprbars' in run('hyprctl', 'plugin', 'list')
    if theme == 'classic98' and plugin.exists():
        if PIN not in run('hyprctl', 'version'):
            print('Classic 98: title bars skipped; rebuild for the updated Hyprland version.', file=sys.stderr)
        elif not loaded:
            run('hyprctl', 'plugin', 'load', str(plugin))
            (STATE / 'plugin-loaded').touch()
    elif loaded and (STATE / 'plugin-loaded').exists():
        run('hyprctl', 'plugin', 'unload', str(plugin))
        (STATE / 'plugin-loaded').unlink()
    run('hyprctl', 'reload')
    errors = run('hyprctl', 'configerrors')
    if errors:
        raise RuntimeError(errors)


def hook(theme):
    active = STATE / 'active'
    switch_backup = STATE / 'before-theme-switch'
    if theme == 'classic98':
        if not active.exists():
            if switch_backup.exists():
                shutil.rmtree(switch_backup)
            snapshot(shell_paths(), switch_backup)
        apply_shell()
        active.touch()
    elif active.exists():
        restore(switch_backup)
        active.unlink()
    decorations(theme)
    run('omarchy', 'restart', 'shell')


def cursor_settings():
    return {key: run('gsettings', 'get', 'org.gnome.desktop.interface', key)
            for key in ('cursor-theme', 'cursor-size')}


def preflight(no_titlebars):
    if not (CONFIG / 'hypr/hyprland.lua').exists():
        raise RuntimeError('An Omarchy installation using hyprland.lua is required.')
    for command in ('omarchy', 'hyprctl', 'gsettings', 'dbus-update-activation-environment'):
        if not shutil.which(command):
            raise RuntimeError(f'Missing command: {command}')
    if STATE.exists() or DATA.exists():
        raise RuntimeError('Classic 98 is already installed. Run the installed uninstall command before reinstalling.')
    for name in ('classic98-shell-hook', 'classic98-titlebar-boot'):
        if list((CONFIG / 'omarchy/hooks').glob('*.d/' + name)):
            raise RuntimeError('A previous development installation exists; restore it before using this installer.')
    for source, target in destinations():
        if target.exists():
            raise RuntimeError(f'Existing theme/plugin would be overwritten: {target}')
    if 'Plugin hyprbars' in run('hyprctl', 'plugin', 'list'):
        raise RuntimeError('An existing hyprbars plugin is loaded; remove it before installing Classic 98.')
    if not no_titlebars:
        if PIN not in run('hyprctl', 'version'):
            raise RuntimeError('Native title bars require Hyprland 0.56.2 at the pinned commit. Use --without-titlebars for the shell, palette and cursors.')
        for command in ('c++', 'make', 'pkg-config'):
            if not shutil.which(command):
                raise RuntimeError(f'Missing {command}. Install build dependencies: sudo pacman -S --needed base-devel hyprland giflib')
        run('pkg-config', '--exists', 'hyprland', 'pixman-1', 'libdrm', 'libinput', 'libudev', 'wayland-server', 'xkbcommon')


def destinations():
    return [(ROOT / 'theme', CONFIG / 'omarchy/themes/classic98'),
            (ROOT / 'cursor-theme/Classic98', HOME / '.local/share/icons/Classic98')] + [
                (p, CONFIG / 'omarchy/plugins' / p.name) for p in sorted((ROOT / 'shell-plugins').iterdir())]


def install(args):
    preflight(args.without_titlebars)
    if args.check:
        print('Preflight passed. No files changed.')
        return
    if args.font:
        if not args.font.is_file():
            raise RuntimeError('The --font path must point to your micross.ttf file.')
        if not shutil.which('fc-cache'):
            raise RuntimeError('fc-cache is required when installing a font.')
    if not args.without_titlebars:
        run('make', '-B', '-C', str(ROOT / 'native-titlebar/hyprbars'), 'CXX=c++',
            'CXXFLAGS=-O2 -fno-gnu-unique -shared -fPIC -std=c++2b -Wno-narrowing', 'EXTRA_FLAGS=')
    previous = {'theme': theme_name(), 'cursor': cursor_settings()}
    if previous['theme'] == 'classic98':
        raise RuntimeError('Select another theme before installing Classic 98.')
    hook_paths = [CONFIG / 'omarchy/hooks' / kind / 'classic98-portable' for kind in ('theme-set.d', 'post-boot.d')]
    paths = [CONFIG / 'hypr/looknfeel.lua', CONFIG / 'hypr/hyprland.lua',
             CONFIG / 'hypr/classic98-cursors.lua', CONFIG / 'uwsm/env',
             HOME / '.local/share/icons/default/index.theme'] + shell_paths() + hook_paths
    if args.font:
        paths.append(HOME / '.local/share/fonts/classic98/micross.ttf')
    snapshot(paths, STATE / 'backup')
    save_json(STATE / 'previous.json', previous)
    save_json(STATE / 'owned.json', [])
    try:
        shutil.copytree(ROOT, DATA, ignore=shutil.ignore_patterns('__pycache__', 'tests', '.git'))
        if args.without_titlebars:
            (DATA / 'native-titlebar/hyprbars/hyprbars.so').unlink(missing_ok=True)
        for source, target in destinations():
            target.parent.mkdir(parents=True, exist_ok=True)
            owned = json.loads((STATE / 'owned.json').read_text())
            owned.append(str(target))
            save_json(STATE / 'owned.json', owned)
            shutil.copytree(source, target)
        original = paths[0].read_text() if paths[0].exists() else ''
        write_text(paths[0], '''-- Classic 98 installer: other themes retain your appearance overrides.
local f = io.open(os.getenv("HOME") .. "/.local/state/omarchy/current/theme.name", "r")
local name = f and f:read("*l") or ""
if f then f:close() end
if name ~= "classic98" then
''' + original + '\nend\n')
        write_text(paths[2], '''hl.env("XCURSOR_THEME", "Classic98")
hl.env("XCURSOR_SIZE", "32")
hl.config({ cursor = { enable_hyprcursor = false } })
hl.exec_cmd("hyprctl setcursor Classic98 32")
''')
        main = paths[1].read_text()
        write_text(paths[1], main + '\nrequire("hypr.classic98-cursors")\n')
        paths[3].parent.mkdir(parents=True, exist_ok=True)
        env = paths[3].read_text() if paths[3].exists() else ''
        write_text(paths[3], env + '\n# Classic 98 cursors\nexport XCURSOR_THEME=Classic98\nexport XCURSOR_SIZE=32\n')
        paths[4].parent.mkdir(parents=True, exist_ok=True)
        write_text(paths[4], '[Icon Theme]\nInherits=Classic98\n')
        if args.font:
            paths[-1].parent.mkdir(parents=True, exist_ok=True)
            if paths[-1].is_symlink():
                paths[-1].unlink()
            shutil.copy2(args.font, paths[-1])
            run('fc-cache', '-f')
        for path in hook_paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            action = 'hook "${1:-}"' if path.parent.name == 'theme-set.d' else 'boot'
            write_text(path, '#!/bin/sh\nexec python3 "$HOME/.local/share/classic98/install.py" ' + action + '\n')
            path.chmod(0o755)
        for key, value in [('cursor-theme', CURSOR), ('cursor-size', '32')]:
            run('gsettings', 'set', 'org.gnome.desktop.interface', key, value)
        run('dbus-update-activation-environment', '--systemd', 'XCURSOR_THEME=Classic98', 'XCURSOR_SIZE=32')
        run('omarchy', 'theme', 'set', 'classic98')
        if not (STATE / 'active').exists():
            hook('classic98')
        run('hyprctl', 'setcursor', CURSOR, '32')
    except Exception:
        print('Installation failed; restoring previous settings.', file=sys.stderr)
        uninstall()
        raise
    print('Classic 98 installed. Reopen apps that cache cursors.')
    print('Uninstall: python3 ~/.local/share/classic98/install.py uninstall')


def uninstall():
    if not (STATE / 'previous.json').exists():
        raise RuntimeError('No installation backup found.')
    previous = json.loads((STATE / 'previous.json').read_text())
    plugin = DATA / 'native-titlebar/hyprbars/hyprbars.so'
    if (STATE / 'plugin-loaded').exists() and 'Plugin hyprbars' in run('hyprctl', 'plugin', 'list'):
        run('hyprctl', 'plugin', 'unload', str(plugin))
    restore(STATE / 'backup')
    if (STATE / 'owned.json').exists():
        for name in json.loads((STATE / 'owned.json').read_text()):
            shutil.rmtree(name, ignore_errors=True)
    for key, value in previous['cursor'].items():
        run('gsettings', 'set', 'org.gnome.desktop.interface', key, value)
    cursor = previous['cursor']['cursor-theme'].strip("'")
    size = previous['cursor']['cursor-size']
    run('dbus-update-activation-environment', '--systemd', f'XCURSOR_THEME={cursor}', f'XCURSOR_SIZE={size}')
    run('omarchy', 'theme', 'set', previous['theme'])
    run('hyprctl', 'reload')
    errors = run('hyprctl', 'configerrors')
    if errors:
        raise RuntimeError(errors)
    run('hyprctl', 'setcursor', cursor, size)
    run('omarchy', 'restart', 'shell')
    # Keep the initial backup available after uninstall.
    import time
    archived = STATE.with_name(f'classic98-uninstalled-backup-{time.time_ns()}')
    STATE.rename(archived)
    shutil.rmtree(DATA, ignore_errors=True)
    print(f'Previous theme and cursor restored. Backup retained: {archived}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', default='install', choices=['install', 'uninstall', 'hook', 'boot'])
    parser.add_argument('theme', nargs='?')
    parser.add_argument('--check', action='store_true', help='Check compatibility without changing files')
    parser.add_argument('--without-titlebars', action='store_true')
    parser.add_argument('--font', type=Path, help='Optional local Microsoft Sans Serif micross.ttf')
    args = parser.parse_args()
    if args.action == 'install':
        install(args)
    elif args.action == 'uninstall':
        uninstall()
    elif args.action == 'boot':
        decorations(theme_name())
    else:
        hook(args.theme or theme_name())


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(f'Classic 98: {error}', file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError):
            print(error.output, file=sys.stderr)
        sys.exit(1)
