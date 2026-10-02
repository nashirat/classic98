from pathlib import Path, PurePosixPath
import json, urllib.request, posixpath
root=Path(__file__).resolve().parent
entries=json.load(open('/tmp/chicago95-tree.json'))['tree']
tree={e['path']:e for e in entries}
sha=json.load(open('/tmp/chicago95-tree.json'))['sha']
base='https://raw.githubusercontent.com/grassmunk/Chicago95/'+sha+'/'
out=root/'theme/icons';out.mkdir(exist_ok=True)
files={}
for name in ['audio-volume-high','audio-volume-medium','audio-volume-low','audio-volume-muted','network-idle','network-offline','bluetooth-active','bluetooth-disabled']:
 files[name+'.png']='Icons/Chicago95/panel/16/'+name+'.png'
for level in ['000','020','040','060','080','100']:
 for suffix in ['', '-charging']:
  name='battery-'+level+suffix+'.png';files[name]='Icons/Chicago95/panel/16/'+name
files.update({'display.png':'Icons/Chicago95/devices/16/video-display.png','computer.png':'Icons/Chicago95/devices/16/computer.png'})
files['windows-start.png']='Theme/Chicago95/misc/windows_16x16px.png'
records=[]
for name,path in files.items():
 original=path
 for _ in range(15):
  data=urllib.request.urlopen(base+path,timeout=20).read()
  if tree[path].get('mode')!='120000': break
  path=posixpath.normpath(posixpath.join(posixpath.dirname(path),data.decode().strip()))
 else: raise RuntimeError('Icon symlink loop')
 if not data.startswith(b'\x89PNG\r\n\x1a\n'):raise RuntimeError('Not a PNG: '+path)
 (out/name).write_bytes(data)
 records.append({'file':name,'source':base+path,'original':original})
(root/'icon-sources.json').write_text(json.dumps({'project':'Chicago95','commit':sha,'homepage':'https://github.com/grassmunk/Chicago95','icons':records},indent=2)+'\n')
credits=urllib.request.urlopen(base+'CREDITS',timeout=20).read()
(out/'Chicago95-CREDITS.txt').write_bytes(credits)
(out/'SOURCES.md').write_text('# Icon sources\n\nSelected 16 px PNG icons from [Chicago95](https://github.com/grassmunk/Chicago95), pinned to commit '+sha+'. See Chicago95-CREDITS.txt and the project icon directories for attribution. Source mappings are in the parent project icon-sources.json. The Start button also uses the classic Windows flag asset from Theme/Chicago95/misc/windows_16x16px.png.\n')
print('Downloaded',len(records),'pixel icons.')
