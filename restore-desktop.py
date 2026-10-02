from pathlib import Path
import shutil, subprocess
root=Path(__file__).resolve().parent
backup=Path((root/'backup-path.txt').read_text().strip())
config=Path.home()/'.config'
for name,target in [('looknfeel.lua',config/'hypr/looknfeel.lua'),('shell.json',config/'omarchy/shell.json'),('shell.toml',config/'omarchy/shell.toml')]:
    shutil.copy2(backup/name,target)
subprocess.run([str(root/'classic98-titlebar-sync'), 'restoring'],check=True)
(config/'omarchy/hooks/post-boot.d/classic98-titlebar-boot').unlink(missing_ok=True)
(config/'omarchy/hooks/theme-set.d/classic98-shell-hook').unlink(missing_ok=True)
(root/'desktop-config/active').unlink(missing_ok=True)
previous=(backup/'previous-theme.txt').read_text().strip()
subprocess.run(['omarchy','theme','set',previous],check=True)
subprocess.run(['hyprctl','reload'],check=True)
subprocess.run(['hyprctl','configerrors'],check=True)
subprocess.run(['omarchy','restart','shell'],check=True)
print('Restored previous desktop settings and theme:',previous)
