# Classic 98 for Omarchy

## Portable installation

The standalone package for another Omarchy PC is
`releases/classic98-omarchy-v1.tar.gz`. See
[portable/README.md](portable/README.md) for compatibility, installation and
uninstall instructions. Build it with `python package-theme.py`; verify the
installer with `python -m unittest discover -s portable -p 'test_*.py'`.
The archive excludes local backups, user config, font binaries and compiled
plugins. This project's older `install-theme.py` is the laptop development
installer; use the archive's `install.py` on another computer.

## Classic cursors and selected workspace texture

`python install-cursors.py --apply` installs and activates the `Classic98`
cursor theme for this user's desktop. It combines Chicago95's original 32 px
and HiDPI 64 px animated-hourglass Xcursor assets, preserving pixels, hotspots,
and frame delays. Source commit and credits live in `cursor-theme/Classic98/`.
The logical cursor size is 32 px. Hyprland uses Xcursor, with GTK settings,
the user default icon theme, and UWSM environment configured consistently.
Previous configuration and cursor settings are saved in
`desktop-config/cursor-backup-*/`. Cursors persist across desktop theme switches.

The selected workspace button has a two-tone silver checker texture inside
its sunken border. Other workspace buttons retain their solid silver fill.

Installed and applied on this machine as `classic98`.

## Appearance

- Opaque silver bottom bar with a raised top seam.
- Raised Start button with the classic Windows flag and numbered workspace buttons; the active workspace is inset.
- Inset clock tray and active-window task button.
- Silver menu, launcher, notification, and dialog surfaces; navy selections and black labels.
- Pure black terminal backgrounds, silver text, and readable blue/green accents.
- Square 4 px gray window borders, small gaps, no blur or window transparency, and a subtle shadow.
- Pattern 167 repeated at its original 128×128 size across a 1280×720 wallpaper, enlarged by the desktop to make the pattern bigger; plain blue and classic teal are included as alternates. The Start button includes the classic Windows flag.

The live compositor uses a gray border, not the browser concept's full beveled title bar. App content colors and app-provided title bars remain under each app's control. The task button shows the active window rather than a complete Windows-style task list.

## Installed files

- `~/.config/omarchy/themes/classic98/`: palette, silver shell surfaces, Hyprland appearance, backgrounds.
- `~/.config/omarchy/plugins/nash.{bar,menu,workspaces,clock,active-window}/`: local copies of Omarchy components with classic chrome. Packaged files are untouched. Visual additions are gated by the theme's `[classic98] enabled` token.
- `~/.config/hypr/looknfeel.lua`: preserves previous personal overrides for other themes and lets Classic 98 supply its own appearance.
- `~/.config/omarchy/hooks/theme-set.d/classic98-shell-hook`: applies this theme's bottom-bar layout and restores the saved previous layout/user shell overrides when switching away.

The hook reads saved layouts from `desktop-config/` in this project. Keep this directory available while using the theme. If you edit the layout while Classic 98 is active, also update `desktop-config/classic-shell.json` so it survives the next theme switch.

## Select the theme or change wallpaper

```bash
omarchy theme set classic98
omarchy theme bg next
```

## Restore the previous desktop

The backup location is recorded in `backup-path.txt`; the initial theme was Volar. Switching themes restores the previous bar layout automatically. To restore the original personal appearance file as well:

```bash
python /home/nash/Work/classic98-theme/restore-desktop.py
```

This keeps the theme and local plugin files available but restores the saved configuration, removes this theme's hook, and selects the previous theme.

## Edit and reinstall

Edit files in `theme/` and `shell-plugins/`, then:

```bash
python /home/nash/Work/classic98-theme/install-theme.py
omarchy theme set classic98
omarchy restart shell
```

The installer uses the existing backup rather than overwriting it.

## Browser concept

```bash
cd /home/nash/Work/classic98-theme
npm install
npm run dev
```

Open http://127.0.0.1:5173. Edit `index.html`, `style.css`, or `main.js` for live updates. `npm run build` creates `dist/`. `preview.html` is the standalone version of the concept.

## Validation

Theme TOML and Lua parsed successfully. The live compositor reports border_size=4, inactive_opacity=1, and enabled shadows, with no Hyprland configuration errors. The local shell components, Menu popup, and bottom bar were checked in desktop screenshots. Browser concept checks cover button states, editor tabs, minimize/restore, backgrounds, progress, and mobile layout.

Theme switching was also verified live: selecting Volar restored the saved bar layout and shell overrides byte-for-byte; selecting Classic 98 again reapplied the theme with no Hyprland errors.

## Pixel icons and tray refinement

The right-side audio, network, power, display, and Bluetooth widgets now use 16 px PNG assets from [Chicago95](https://github.com/grassmunk/Chicago95). Audio mute/level, network connected/disconnected, power charge/level, and Bluetooth on/off retain their state behavior. The right section shares an inset housing with the clock; Start has the classic Windows flag icon and a narrow grip divider. Local cloned widgets preserve their original panel controls.

The exact asset URLs and pinned upstream commit are in icon-sources.json. Attribution is included in theme/icons/. [Alex Meub's original Windows 98 viewer](https://win98icons.alexmeub.com/) is another reference for original assets.

The shell hook now restarts the shell after changing bar implementations. Without this, the replacement-bar hot reload could leave the live bar empty even though the config and Hyprland validation passed.

## Native tiled title bars

Classic 98 now loads a locally built adaptation of the official [hyprbars](https://github.com/hyprwm/hyprland-plugins/tree/main/hyprbars) plugin. Each tile has a 26 px title strip: navy and white when focused, gray when inactive, with square raised silver close and maximize controls. Double-click the title to toggle maximize. Pure black app interiors and the silver border remain.

The theme-set hook loads this plugin for Classic 98 and unloads it for other themes. A post-boot hook restores it at login. The native title bar uses the browser preview’s navy-to-light-blue gradient (#000080 → #164bdc), with gray gradients for inactive windows; application File/Edit menus and toolbars remain application-owned. The `_` button hides the window in the scratchpad; Super+S shows it again. The square button maximizes and changes into overlapping squares while maximized, which restore the normal tile size. `×` closes the window.

Source and build notes are in `native-titlebar/CLASSIC98.md`. This build matches Hyprland 0.56.2; after a Hyprland update, rebuild from the upstream commit matching the new version and its installed headers. The plugin retains the upstream ABI check. Run `./classic98-titlebar-sync` to load it and reload its configuration after rebuilding.

Desktop bar height increased from 32 px to 36 px; raised and inset widgets grow with the bar.

The desktop bar has no center widgets or agent widget. These layout changes persist when Classic 98 is selected again.

Matching grip dividers frame the workspace buttons. The active-window title widget is removed; native tile headers show window titles.

Desktop bar spacing: 40 px total height, with 5 px above and below the native raised controls and tray housing.

Divider grips retain their left spacing and reserve an extra 4 px on the right for balanced separation from the next control.

Right-side tray icons render at 20 px in 26 px slots (6 px between icons), with smoothing disabled to preserve pixel edges.

Classic controls and tile headers request Microsoft Sans Serif. It requires the genuine micross.ttf font installed locally; until then fontconfig falls back to Liberation Sans. The font file is not bundled.

Microsoft Sans Serif is installed in the user font directory. Its source and verified checksums are recorded in font-source.json; no font binary is bundled in the theme. Foot uses a black-on-silver relative scrollback indicator with a percentage label. This is an indicator, not a full beveled scrollbar; new Foot windows load this setting.

Foot font restored to JetBrainsMono Nerd Font size 14 after Omarchy’s font picker reset it to 9. The scrollback indicator uses gray colors with its original default behavior, without the added percentage label.

## Pattern 167 wallpaper

Original tile: https://cs.gettysburg.edu/~duncjo01/assets/images/patterns/167.png. Full-size repeats are saved in `/home/nash/Work/wallp/` at 1280×720, 1920×1080, and 2880×1800. The installed theme uses 1280×720, which fills the display and enlarges the pattern. The browser preview uses the original tile with CSS repetition.

## Start shortcuts and centered workspaces

Four 20 px classic icons in 26 px slots sit beside Start, matching the tray: Internet Explorer opens Chrome; email opens Gmail in Chrome; Paint is reserved for Figma; phone opens WhatsApp Web in Chrome. Workspaces 1–5 sit at the center of the bar with grip dividers on both sides. The `nash.quick-icons` widget and layout are stored in this project so theme changes preserve them.

Quick-launch replacements: Gmail uses Outlook Express’s blue e + envelope; Figma uses the Kodak Imaging framed picture; WhatsApp uses the Channels satellite dish. Start uses Microsoft Sans Serif with synthesized bold, the scalable successor of the original MS Sans Serif bitmap font.

Agent tile headers replace their leading Braille activity spinner with an animated Windows hourglass from the original Tenor GIF. Idle titles show their normal text again. The asset is loaded relative to the plugin, and source attribution/timing tests are recorded under native-titlebar.

Start’s icon/text gap is tightened to 5 px; its native button is 4 px narrower while keeping the outer padding and divider spacing.

Omarchy menus and the app launcher use opaque black backgrounds, 4 px silver borders, light-gray text, and gray selected rows with black text.

Menu/launcher selection is a flat near-white #e6e6e6 highlight with black text, zero selection-border width, and zero selection-border alpha.

Classic menu cards have a 26 px Menu title strip with the tile header’s #000080 → #164bdc gradient, white Microsoft Sans Serif text, and no window controls. Near-white menu/launcher selections render at 90% opacity.

Classic98 boot/disk-unlock and shutdown dialogs are provided separately in [boot-screen](boot-screen/README.md), with [unlock](boot-screen/preview-unlock.png) and [shutdown](boot-screen/preview-shutdown.png) previews. The separate system Plymouth theme was installed and the Limine UKI rebuilt successfully. This choice does not follow desktop theme switching automatically.
