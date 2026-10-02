#!/usr/bin/env python3
"""Create the portable Classic 98 distribution, excluding local state."""
from pathlib import Path
import hashlib
import shutil
import tarfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'releases'
STAGE = OUT / 'classic98-omarchy-v1'
if STAGE.exists():
    shutil.rmtree(STAGE)
STAGE.mkdir(parents=True, exist_ok=True)
for name in ('theme', 'shell-plugins', 'cursor-theme'):
    shutil.copytree(ROOT / name, STAGE / name)
for name in ('install.py', 'README.md', 'OMARCHY-LICENSE'):
    shutil.copy2(ROOT / 'portable' / name, STAGE / name)
shutil.copy2(ROOT / 'desktop-config/classic-shell.json', STAGE / 'layout.json')
native = STAGE / 'native-titlebar'
native.mkdir()
for name in ('LICENSE', 'CLASSIC98.md'):
    shutil.copy2(ROOT / 'native-titlebar' / name, native / name)
shutil.copytree(ROOT / 'native-titlebar/assets', native / 'assets')
shutil.copytree(ROOT / 'native-titlebar/hyprbars', native / 'hyprbars',
                ignore=shutil.ignore_patterns('*.so', '*.o', 'build', '.git'))
sources = STAGE / 'sources'
sources.mkdir()
for name in ('icon-sources.json', 'font-source.json'):
    shutil.copy2(ROOT / name, sources / name)
archive = OUT / (STAGE.name + '.tar.gz')
with tarfile.open(archive, 'w:gz') as bundle:
    bundle.add(STAGE, arcname=STAGE.name)
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix(archive.suffix + '.sha256').write_text(f'{digest}  {archive.name}\n')
print(f'Package: {archive}\nSHA256: {digest}')
