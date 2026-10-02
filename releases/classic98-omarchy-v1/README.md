# Classic 98 for Omarchy

An installable desktop theme with silver window frames, blue gradient title
bars, a bottom taskbar, pixel tray and quick-launch icons, animated hourglass
cursors, and a silver checker pattern on the selected workspace.

## Install on another computer

Extract this archive and open a terminal in its directory. This requires the
Lua-based Omarchy release (the system has `~/.config/hypr/hyprland.lua`) and a
running desktop session. No root access is required by the theme installer.

Native title bars currently support **Hyprland 0.56.2**, commit
`efb50993780079460b0cbed1363e2166a2de1d9f`. They are compiled on the receiving
computer, never copied as a laptop-specific binary. Install build dependencies
if necessary:

```bash
sudo pacman -S --needed base-devel hyprland giflib
python3 install.py --check
python3 install.py
```

On a different Hyprland version, install the palette, widgets and cursors
without native title bars:

```bash
python3 install.py --check --without-titlebars
python3 install.py --without-titlebars
```

Shell plugins use the current Omarchy `qs.Commons`, `qs.Ui` and plugin APIs.
The installer checks basic prerequisites; future shell API changes can require
an updated package. The plugin's own ABI check also guards native title bars.

Microsoft Sans Serif is optional. If you have `micross.ttf` locally:

```bash
python3 install.py --font /path/to/micross.ttf
```

The font binary is not included. Otherwise the system selects a fallback sans
font. Code fonts and display scaling retain the receiving PC's settings.

Restart apps that cache cursor themes after installing. Cursor changes are
global and persist when you select another desktop theme. They are restored
when uninstalling.

## Switch themes and uninstall

```bash
omarchy theme set classic98
omarchy theme set YOUR_OTHER_THEME
python3 ~/.local/share/classic98/install.py uninstall
```

Selecting Classic 98 applies its bar layout and shell appearance. Selecting
another theme restores the shell configuration saved when Classic 98 was
activated. Existing idle/lock settings are preserved. The initial user
configuration and cursor settings are backed up under
`~/.local/state/classic98-installer/`. Uninstall restores that initial snapshot
and keeps an archived backup. It restores the initial files in full, so save
any later edits to those files before uninstalling.

Existing `classic98` themes, `Classic98` cursors, or `nash.*` plugin names owned
by this package cause installation to stop rather than overwrite them. The
`nash.*` names are plugin identifiers; installation works under any username.
To reinstall or upgrade, uninstall the previous portable installation first.

This is a full desktop package: `omarchy theme install <url>` alone installs
only a theme's palette/assets and will not install its plugins and hooks.

## Included and separate components

Included: app palette, opaque silver bar, Start/launcher styling, workspace
controls, checker texture, clock and tray panels, quick-launch shortcuts,
wallpapers, normal/HiDPI classic cursors, native title-bar source and busy
hourglass asset. The minimize button hides windows in the existing scratchpad;
Super+S restores that workspace. Quick-launch shortcuts target the browser,
Gmail and WhatsApp; the image-editor shortcut is currently a placeholder.

The Plymouth boot/unlock screen is a separate system customization and is not
installed by this package. Application interiors and toolbars remain under
each application's control. Full window task buttons and an anchored Start
menu have not been implemented.

## Sources and attribution

- Shell widgets adapted from [Omarchy](https://github.com/basecamp/omarchy).
- Native decorations adapted from
  [hyprland-plugins](https://github.com/hyprwm/hyprland-plugins), commit
  `7644cecdb947060682891a0db2a0cdc5c0b9e704`; license in `native-titlebar/LICENSE`.
- Cursors and icons from [Chicago95](https://github.com/grassmunk/Chicago95);
  credits and pinned cursor sources in `cursor-theme/Classic98/`, icon mappings
  in `sources/`. Pixels, hotspots and animation delays are preserved when
  combining the 32 px and 64 px cursor variants.
- Hourglass asset: source page and checksum in
  `native-titlebar/assets/hourglass-source.json`.
- Pattern 167 wallpaper: original tile from
  https://cs.gettysburg.edu/~duncjo01/assets/images/patterns/167.png.

Existing source licenses and asset attribution apply to their components.
