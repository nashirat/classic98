from pathlib import Path
import re, shutil, struct, zlib, tomllib
root = Path(__file__).resolve().parent
theme = root / 'theme'
theme.mkdir(exist_ok=True)
shutil.copy2(root / 'colors.toml', theme / 'colors.toml')
# A separate chrome palette keeps app and terminal backgrounds truly black.
source = Path('/home/nash/.config/omarchy/themes/volar/shell.toml').read_text()
sections = tomllib.loads(source)
for name, values in sections.items():
    if 'background' in values: values['background'] = '#c0c0c0'
    if 'text' in values: values['text'] = '#000000'
    for key in list(values):
        if key.endswith('alpha'): values[key] = 1.0
        if key == 'scrim-alpha': values[key] = 0.0
        if key in ('border', 'normal-border', 'hover-cursor-border', 'focus-border'): values[key] = '#808080'
        if key == 'selected-background': values[key] = '#000080'
        if key == 'selected-text': values[key] = '#ffffff'
        if key == 'selected-border': values[key] = '#000080'
        if key == 'selected-color': values[key] = '#000080'
        if key in ('normal-color','hover-cursor-color','focus-color'): values[key] = '#000000'
sections['bar'].update({'size-horizontal':36,'scale-with-font':False,'active':'#000080'})
sections['hyprland'].update({'active-border':'#c0c0c0','active-border-foreground':'#000000'})
sections['controls'].update({'normal-fill-alpha':0.0,'hover-cursor-fill-alpha':0.08,'focus-fill-alpha':0.08,'selected-fill-alpha':0.16,'pressed-fill-alpha':0.16,'selection-fill-alpha':1.0,'normal-border-alpha':1.0,'hover-cursor-border-alpha':1.0,'focus-border-alpha':1.0})
sections['classic98'] = {'enabled':'true'}
sections['font']['base-size'] = 12
sections['spacing'].update({'scale':1.0,'scale-with-font':False,'control-height':26,'control-padding-y':4,'control-padding-x':10})
for name in ('popups','notifications','menu','launcher','polkit','lock'):
    sections[name]['border-width'] = 2
sections['tooltip'].update({'background':'#ffffe1','text':'#000000','border':'#000000','border-width':1})
sections['notifications']['countdown']='#000080'
sections['lock'].update({'selection':'#000080','placeholder':'#404040','border-active':'#000080','text-error':'#800000'})
sections['polkit'].update({'accent':'#000080','text-error':'#800000','border-error':'#800000'})
def literal(value):
    if isinstance(value,bool): return str(value).lower()
    if isinstance(value,str): return '"'+value+'"'
    return str(value)
(theme/'shell.toml').write_text('# Classic 98 / opaque silver shell chrome\n\n'+'\n\n'.join('['+name+']\n'+'\n'.join(key+' = '+literal(value) for key,value in values.items()) for name,values in sections.items())+'\n')
(theme/'hyprland.lua').write_text('''-- Classic 98: black apps, square silver borders, a small drop shadow.
hl.config({
  general = {
    border_size = 4,
    gaps_in = 6,
    gaps_out = 12,
    col = { active_border = "rgb(c0c0c0)", inactive_border = "rgb(808080)" },
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
    col = { border_active = "rgb(c0c0c0)", border_inactive = "rgb(808080)" },
    groupbar = { text_color = "rgb(ffffff)", text_color_inactive = "rgb(000000)",
      col = { active = "rgb(000080)", inactive = "rgb(c0c0c0)" } },
  },
})
-- Last matching rule wins. Apply to all app windows, including unfocused ones.
o.window(".*", { opacity = "1.0 override 1.0 override 1.0 override", no_blur = true })
''')
# Plain blue as a temporary background; classic teal is an alternate.
# These are solid-color swatches, not copies of reference-image pixels.
def png(path, rgb):
    w,h=1920,1080
    raw=(b'\0'+bytes(rgb)*w)*h
    def chunk(kind,data): return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
(theme/'backgrounds').mkdir(exist_ok=True)
png(theme/'backgrounds'/'01-classic-blue.png',(0,0,168))
png(theme/'backgrounds'/'02-classic-teal.png',(0,128,128))
for name in ('colors.toml','shell.toml'):
    tomllib.loads((theme/name).read_text())
print('Built theme:',theme)
