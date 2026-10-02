#!/usr/bin/env python3
"""Build and optionally install classic cursors from pinned Chicago95 assets."""
import argparse
import json
from pathlib import Path
import shutil
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parent
NAME = 'Classic98'
SIZE = 32
UPSTREAM = ROOT / 'cursor-upstream'
DEST = ROOT / 'cursor-theme' / NAME


def merge_cursors(paths):
    entries = []
    for path in paths:
        data = path.read_bytes()
        magic, header, version, count = struct.unpack_from('<4I', data)
        assert magic == 0x72756358 and header == 16
        for i in range(count):
            kind, size, offset = struct.unpack_from('<3I', data, header + i * 12)
            chunk_header, chunk_kind, chunk_size, _ = struct.unpack_from('<4I', data, offset)
            assert kind == chunk_kind == 0xfffd0002 and size == chunk_size
            width, height = struct.unpack_from('<2I', data, offset + 16)
            chunk = data[offset:offset + chunk_header + width * height * 4]
            entries.append((kind, size, chunk))
    offset = 16 + 12 * len(entries)
    result = bytearray(struct.pack('<4I', magic, 16, version, len(entries)))
    for kind, size, chunk in entries:
        result.extend(struct.pack('<3I', kind, size, offset))
        offset += len(chunk)
    for _, _, chunk in entries:
        result.extend(chunk)
    return result


def build():
    variants = [UPSTREAM / 'Cursors' / name / 'cursors' for name in (
        'Chicago95_Animated_Hourglass_Cursors',
        'Chicago95_Animated_Hourglass_Cursors_HiDPI')]
    (DEST / 'cursors').mkdir(parents=True, exist_ok=True)
    names = sorted({p.name for folder in variants for p in folder.iterdir() if p.is_file()})
    for name in names:
        paths = [folder / name for folder in variants if (folder / name).is_file()]
        (DEST / 'cursors' / name).write_bytes(merge_cursors(paths))
    (DEST / 'index.theme').write_text('[Icon Theme]\nName=Classic 98\nComment=Classic pixel cursors with animated hourglass and 32/64 px assets\nInherits=Adwaita\n')
    commit = subprocess.check_output(['git', '-C', str(UPSTREAM), 'rev-parse', 'HEAD'], text=True).strip()
    (DEST / 'SOURCES.json').write_text(json.dumps({
        'repository': 'https://github.com/grassmunk/Chicago95', 'commit': commit,
        'variants': [str(p.relative_to(UPSTREAM)) for p in variants],
        'adaptation': 'Combine original 32 and 64 px Xcursor frames; preserve pixels, hotspots and delays.'
    }, indent=2) + '\n')
    shutil.copy2(UPSTREAM / 'CREDITS', DEST / 'CREDITS')
    print(f'Built {len(names)} cursor names with original animation frames: {DEST}')


def install():
    home = Path.home()
    config = home / '.config'
    paths = [config / 'hypr/hyprland.lua', config / 'hypr/classic98-cursors.lua',
             config / 'uwsm/env', home / '.local/share/icons/default/index.theme']
    backup = ROOT / 'desktop-config' / f'cursor-backup-{int(time.time())}'
    backup.mkdir(parents=True)
    for i, path in enumerate(paths):
        if path.exists():
            shutil.copy2(path, backup / str(i))
    previous = {key: subprocess.check_output(['gsettings', 'get', 'org.gnome.desktop.interface', key], text=True).strip()
                for key in ('cursor-theme', 'cursor-size')}
    (backup / 'settings.json').write_text(json.dumps({'paths': [str(p) for p in paths], 'gsettings': previous}, indent=2))
    shutil.copytree(DEST, home / '.local/share/icons' / NAME, dirs_exist_ok=True)
    paths[3].parent.mkdir(parents=True, exist_ok=True)
    paths[3].write_text(f'[Icon Theme]\nInherits={NAME}\n')
    paths[1].write_text(f'''-- Classic pixel cursor set, installed by classic98-theme/install-cursors.py.
hl.env("XCURSOR_THEME", "{NAME}")
hl.env("XCURSOR_SIZE", "{SIZE}")
hl.config({{ cursor = {{ enable_hyprcursor = false }} }})
hl.exec_cmd("hyprctl setcursor {NAME} {SIZE}")
''')
    main = paths[0].read_text()
    if 'require("hypr.classic98-cursors")' not in main:
        paths[0].write_text(main + '\nrequire("hypr.classic98-cursors")\n')
    paths[2].parent.mkdir(parents=True, exist_ok=True)
    env = paths[2].read_text() if paths[2].exists() else ''
    paths[2].write_text(env + f'\n# Classic 98 cursors\nexport XCURSOR_THEME={NAME}\nexport XCURSOR_SIZE={SIZE}\n')
    for key, value in [('cursor-theme', NAME), ('cursor-size', str(SIZE))]:
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', key, value], check=True)
    subprocess.run(['hyprctl', 'reload'], check=True)
    errors = subprocess.check_output(['hyprctl', 'configerrors'], text=True).strip()
    if errors:
        raise RuntimeError(errors)
    subprocess.run(['hyprctl', 'setcursor', NAME, str(SIZE)], check=True)
    subprocess.run(['dbus-update-activation-environment', '--systemd', f'XCURSOR_THEME={NAME}', f'XCURSOR_SIZE={SIZE}'], check=True)
    print(f'Applied {NAME} at {SIZE} px. Backup: {backup}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    build()
    if args.apply:
        install()
