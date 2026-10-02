# Classic 98 title-bar adaptation

Based on https://github.com/hyprwm/hyprland-plugins at commit 7644cecdb947060682891a0db2a0cdc5c0b9e704, the upstream pin for Hyprland 0.56.2 (efb50993780079460b0cbed1363e2166a2de1d9f).

Local change: renderBarButtons uses square silver controls with top/left white highlights and bottom/right dark edges. Upstream title, click, drag, and decoration behavior is retained. The title-bar colors come from the theme configuration. `bar_gradient` enables a cached 256×1 texture ramp; `bar_gradient_color` and `inactive_gradient_color` set its right endpoint for focused and inactive windows. The start color retains upstream rule and animation behavior. Classic 98 uses #000080 → #164bdc and #808080 → #b5b5b5 to match the browser preview.

The plugin must be rebuilt for a future Hyprland ABI. The upstream initialization checks the header/client hash before attaching decorations.

Build: make -C hyprbars CXX=c++ CXXFLAGS='-O2 -fno-gnu-unique -shared -fPIC -std=c++2b -Wno-narrowing'

Classic window controls are drawn as pixel geometry: `_` hides to `special:scratchpad`; the square toggles maximize and shows two overlapping squares while maximized. Super+S toggles the existing scratchpad to restore hidden windows. Live checks verified maximize/restore and scratchpad hide/show; Hyprland config errors are empty.

Animated busy indicator: hourglass.hpp decodes the original Tenor GIF via giflib. On org.omarchy.agent windows and legacy Foot agent titles containing " | ", a leading Braille character plus space is replaced with an 18 px nearest-filtered animated hourglass. GIF delays drive frame selection; the decoration schedules 50 ms redraws only while busy and visible and removes its timer on destruction/unload. The original GIF is unchanged; edge-connected near-white background is omitted while enclosed white glass/sand remains. Missing/invalid GIF falls back to the original title. The asset lives beside hyprbars in ../assets; dladdr locates it relative to the loaded plugin. Build also links giflib and libdl.

Decode/state tests: `c++ -std=c++23 -fsanitize=address,undefined tests/hourglass-test.cpp -o /tmp/classic98-hourglass-test -lgif -ldl` then `ASAN_OPTIONS=detect_leaks=0 /tmp/classic98-hourglass-test assets/hourglass-original.gif`. Leak detection is disabled in the sandbox because ptrace prevents LeakSanitizer; address and undefined-behavior checks remain enabled. Tests cover agent-only matching, busy/idle title stripping, frame timing/looping, retained interior white, transparent outer background, and missing assets.

Build into a new binary and unload before replacing a running plugin. The pre-hourglass plugin is backed up in backups/before-hourglass.
