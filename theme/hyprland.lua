-- Classic 98: black apps, square silver borders, a small drop shadow.
hl.config({
  general = {
    border_size = 4,
    gaps_in = 6,
    gaps_out = 12,
    col = { active_border = "rgb(e4e4e4)", inactive_border = "rgb(a0a0a0)" },
  },
  decoration = {
    rounding = 0,
    active_opacity = 1.0,
    inactive_opacity = 1.0,
    fullscreen_opacity = 1.0,
    dim_inactive = false,
    blur = { enabled = false },
    shadow = { enabled = true, range = 6, render_power = 3, color = "rgba(00000066)", offset = { 2, 3 } },
  },
  group = {
    col = { border_active = "rgb(e4e4e4)", border_inactive = "rgb(a0a0a0)" },
    groupbar = { text_color = "rgb(ffffff)", text_color_inactive = "rgb(000000)",
      col = { active = "rgb(000080)", inactive = "rgb(c0c0c0)" } },
  },
})
-- Last matching rule wins. Apply to all app windows, including unfocused ones.
o.window(".*", { opacity = "1.0 override 1.0 override 1.0 override", no_blur = true })

-- The boot/theme hook loads the version-matched native decoration first.
if hl.plugin.hyprbars ~= nil then
  hl.config({ plugin = { hyprbars = {
    enabled = true,
    bar_height = 20,
    bar_color = "rgb(8f9f8f)",
    bar_gradient = false,
    bar_blur = false,
    col = { text = "rgb(000000)" },
    bar_text_size = 12,
    bar_text_weight = "bold",
    bar_text_font = "Microsoft Sans Serif",
    bar_text_align = "center",
    bar_part_of_window = true,
    bar_precedence_over_border = true,
    bar_padding = 4,
    bar_button_padding = 3,
    inactive_button_color = "rgb(c0c0c0)",
    on_double_click = [[hyprctl dispatch 'hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" })']],
  } } })
  -- The fvwm-style beveled frame (borders-plus-plus fork) replaces the flat border.
  -- ponytail: assumes it loads alongside hyprbars; it has no Lua table to check.
  hl.config({ general = { border_size = 0 } })
  hl.plugin.hyprbars.add_button({
    bg_color = "rgb(c0c0c0)", fg_color = "rgb(000000)", size = 14,
    icon = "×", action = "hyprctl dispatch 'hl.dsp.window.close()'",
  })
  hl.plugin.hyprbars.add_button({
    bg_color = "rgb(c0c0c0)", fg_color = "rgb(000000)", size = 14,
    icon = "□",
    action = [[hyprctl dispatch 'hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" })']],
  })
  hl.plugin.hyprbars.add_button({
    bg_color = "rgb(c0c0c0)", fg_color = "rgb(000000)", size = 14,
    icon = "_",
    action = [[hyprctl dispatch 'hl.dsp.window.move({ workspace = "special:scratchpad", follow = false })']],
  })
  o.window({ focus = false }, {
    ["hyprbars:bar_color"] = "rgb(003c3c)",
    ["hyprbars:title_color"] = "rgb(ffffff)",
  })
end
