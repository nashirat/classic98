from pathlib import Path
import shutil, json, subprocess
root=Path(__file__).resolve().parent
config=Path.home()/'.config'
backup=Path((root/'backup-path.txt').read_text().strip())
# Install only user-owned theme and plugin files.
target=config/'omarchy/themes/classic98'
shutil.copytree(root/'theme',target,dirs_exist_ok=True)
for source in (root/'shell-plugins').iterdir():
    shutil.copytree(source,config/'omarchy/plugins'/source.name,dirs_exist_ok=True)
# The user's opacity and border overrides otherwise defeat the new theme.
original=(backup/'looknfeel.lua').read_text()
look='''-- Classic 98 lets its theme supply geometry/opacity. Other themes retain your previous appearance overrides.
local theme_file = io.open(os.getenv("HOME") .. "/.local/state/omarchy/current/theme.name", "r")
local theme_name = theme_file and theme_file:read("*l") or ""
if theme_file then theme_file:close() end
if theme_name ~= "classic98" then
'''+original+'\nend\n'
(config/'hypr/looknfeel.lua').write_text(look)
state=root/'desktop-config'
state.mkdir(exist_ok=True)
# Base layout includes all existing widgets; move the clock into the inset tray end.
layout=json.loads((state/'classic-shell.json').read_text()) if (state/'classic-shell.json').exists() else json.loads((config/'omarchy/shell.json').read_text())
bar=layout['bar']
bar['id']='nash.bar';bar['position']='bottom';bar['transparent']=False;bar['centerAnchor']=''
bar['layout']['left']=[entry for entry in bar['layout']['left'] if entry['id']!='nash.active-window']
center=bar['layout']['center']
clock=next(entry for entry in center+bar['layout']['right'] if entry['id']=='nash.clock')
clock.update({'format':'h:mm AP','formatAlt':'ddd d MMM HH:mm'})
bar['layout']['center']=[]
bar['layout']['right']=[entry for entry in bar['layout']['right'] if entry['id'] not in ('nash.clock', 'omarchy.agents')]
bar['layout']['right'].append(clock)
(state/'classic-shell.json').write_text(json.dumps(layout,indent=2)+'\n')
(state/'classic-shell.toml').write_text('# Classic 98 uses theme-supplied surface borders and sizes.\n[font]\nbase-size = 12\n')
shutil.copy2(backup/'shell.json',state/'previous-shell.json')
shutil.copy2(backup/'shell.toml',state/'previous-shell.toml')
# Theme-specific layout/user overrides restore automatically when another theme is selected.
hook=root/'classic98-shell-hook'
hook.chmod(0o755)
subprocess.run(['omarchy','hook','install','theme-set',str(hook)],check=True)
subprocess.run(['omarchy','hook','install','post-boot',str(root/'classic98-titlebar-boot')],check=True)
# The theme hook restarts the shell after the complete layout is written.
print('Installed Classic 98. Backup:',backup)
