import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

STAGE = Path(__file__).resolve().parents[1] / 'releases/classic98-omarchy-v1'


class PortableInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='classic98-test-')
        spec = importlib.util.spec_from_file_location('installer', STAGE / 'install.py')
        self.app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.app)
        app = self.app
        app.HOME = Path(self.temp.name)
        app.CONFIG = app.HOME / '.config'
        app.DATA = app.HOME / '.local/share/classic98'
        app.STATE = app.HOME / '.local/state/classic98-installer'
        app.CONFIG.joinpath('hypr').mkdir(parents=True)
        self.main = app.CONFIG / 'hypr/hyprland.lua'
        self.main.write_text('-- original main\n')
        self.look = app.CONFIG / 'hypr/looknfeel.lua'
        self.look.write_text('-- original appearance\n')
        app.CONFIG.joinpath('omarchy').mkdir()
        self.shell = app.CONFIG / 'omarchy/shell.json'
        self.original_shell = {'version': 1, 'idle': {'lock': 777}, 'bar': {'id': 'omarchy.bar', 'transparent': True},
                               'plugins': [{'id': 'my.plugin'}]}
        self.shell.write_text(json.dumps(self.original_shell))
        self.shell_bytes = self.shell.read_bytes()
        self.theme_file = app.HOME / '.local/state/omarchy/current/theme.name'
        self.theme_file.parent.mkdir(parents=True)
        self.theme_file.write_text('volar\n')
        self.cursor = {'cursor-theme': "'Adwaita'", 'cursor-size': '24'}
        self.fail_install = False
        self.loaded = False
        self.native = True
        self.calls = []
        self.patches = [patch.object(app, 'run', self.command), patch.object(app.shutil, 'which', return_value='/usr/bin/mock')]
        for mock in self.patches:
            mock.start()

    def tearDown(self):
        for mock in self.patches:
            mock.stop()
        self.temp.cleanup()

    def command(self, *args):
        self.calls.append(args)
        if args[:2] == ('hyprctl', 'version'):
            return self.app.PIN if self.native else 'different-version'
        if args[:3] == ('hyprctl', 'plugin', 'list'):
            return 'Plugin hyprbars' if self.loaded else ''
        if args[:3] == ('hyprctl', 'plugin', 'load'):
            self.loaded = True
        if args[:3] == ('hyprctl', 'plugin', 'unload'):
            self.loaded = False
        if args[:2] == ('gsettings', 'get'):
            return self.cursor[args[-1]]
        if args[:2] == ('gsettings', 'set'):
            self.cursor[args[-2]] = args[-1]
        if args[:3] == ('omarchy', 'theme', 'set'):
            if args[-1] == 'classic98' and self.fail_install:
                raise subprocess.CalledProcessError(1, args, output='injected activation failure')
            self.theme_file.write_text(args[-1] + '\n')
            if (self.app.DATA / 'install.py').exists() and (self.app.CONFIG / 'omarchy/hooks/theme-set.d/classic98-portable').exists():
                self.app.hook(args[-1])
        return ''

    def args(self, **kwargs):
        return argparse.Namespace(check=False, without_titlebars=True, font=None, **kwargs)

    def test_check_changes_nothing(self):
        args = self.args()
        args.check = True
        before = sorted(str(p) for p in self.app.HOME.rglob('*'))
        self.app.install(args)
        self.assertEqual(before, sorted(str(p) for p in self.app.HOME.rglob('*')))

    def test_install_switch_restore_and_uninstall(self):
        self.app.install(self.args())
        installed = json.loads(self.shell.read_text())
        self.assertFalse(installed['bar']['transparent'])
        self.assertEqual(installed['idle']['lock'], 777)
        self.assertIn({'id': 'my.plugin'}, installed['plugins'])
        self.assertIn({'id': 'nash.osd'}, installed['plugins'])
        self.assertTrue((self.app.CONFIG / 'omarchy/plugins/nash.workspaces/checker.svg').exists())
        self.app.hook('volar')
        self.assertEqual(self.shell.read_bytes(), self.shell_bytes)
        # Snapshot a later edit on another theme rather than overwriting it.
        changed = dict(self.original_shell, idle={'lock': 999})
        self.shell.write_text(json.dumps(changed))
        self.app.hook('classic98')
        self.app.hook('classic98')
        self.app.hook('volar')
        self.assertEqual(json.loads(self.shell.read_text()), changed)
        self.app.uninstall()
        self.assertEqual(self.shell.read_bytes(), self.shell_bytes)
        self.assertEqual(self.look.read_text(), '-- original appearance\n')
        self.assertEqual(self.main.read_text(), '-- original main\n')
        self.assertFalse((self.app.CONFIG / 'uwsm/env').exists())
        self.assertFalse(self.app.DATA.exists())
        self.assertEqual(self.cursor, {'cursor-theme': "'Adwaita'", 'cursor-size': '24'})

    def test_activation_failure_rolls_back(self):
        self.fail_install = True
        with self.assertRaises(subprocess.CalledProcessError):
            self.app.install(self.args())
        self.assertEqual(self.shell.read_bytes(), self.shell_bytes)
        self.assertEqual(self.main.read_text(), '-- original main\n')
        self.assertFalse(self.app.DATA.exists())
        self.assertFalse(self.app.STATE.exists())

    def test_refuses_existing_plugin_without_changes(self):
        existing = self.app.CONFIG / 'omarchy/plugins/nash.menu'
        existing.mkdir(parents=True)
        with self.assertRaisesRegex(RuntimeError, 'overwritten'):
            self.app.install(self.args())
        self.assertTrue(existing.exists())
        self.assertFalse(self.app.STATE.exists())

    def test_wrong_native_version_fails_before_writes(self):
        self.native = False
        args = self.args()
        args.without_titlebars = False
        with self.assertRaisesRegex(RuntimeError, '0.56.2'):
            self.app.install(args)
        self.assertFalse(self.app.STATE.exists())

    def test_second_install_preserves_backup(self):
        self.app.install(self.args())
        before = (self.app.STATE / 'previous.json').read_bytes()
        with self.assertRaisesRegex(RuntimeError, 'already installed'):
            self.app.install(self.args())
        self.assertEqual(before, (self.app.STATE / 'previous.json').read_bytes())

    def test_symlink_backup_restores_symlink(self):
        target = self.app.HOME / 'shared-config'
        target.write_text('shared')
        self.look.unlink()
        self.look.symlink_to(target)
        directory = self.app.HOME / 'snapshot'
        self.app.snapshot([self.look], directory)
        self.look.unlink()
        self.look.write_text('replacement')
        self.app.restore(directory)
        self.assertTrue(self.look.is_symlink())
        self.assertEqual(self.look.resolve(), target)

    def test_install_does_not_change_linked_config_target(self):
        target = self.app.HOME / 'shared-main.lua'
        target.write_text('-- shared original\n')
        self.main.unlink()
        self.main.symlink_to(target)
        self.app.install(self.args())
        self.assertEqual(target.read_text(), '-- shared original\n')
        self.app.uninstall()
        self.assertTrue(self.main.is_symlink())
        self.assertEqual(target.read_text(), '-- shared original\n')


if __name__ == '__main__':
    unittest.main()
