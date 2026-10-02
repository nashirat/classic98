from pathlib import Path
import subprocess
root = Path(__file__).resolve().parent
font = str(Path.home()/'.local/share/fonts/classic98/micross.ttf')
def render(name, title, message, detail):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="260">
    <defs><linearGradient id="title"><stop stop-color="#000080"/><stop offset="1" stop-color="#164bdc"/></linearGradient></defs>
    <rect width="640" height="260" fill="#c0c0c0"/>
    <path d="M0 259V0H639" stroke="white" stroke-width="2" fill="none"/>
    <path d="M639 1V259H1" stroke="#000000" stroke-width="2" fill="none"/>
    <path d="M637 3V257H3" stroke="#808080" stroke-width="2" fill="none"/>
    <rect x="5" y="5" width="630" height="34" fill="url(#title)"/>
    <g font-family="Microsoft Sans Serif" font-size="18" fill="black">
    <text x="14" y="29" fill="white" font-weight="bold">{title}</text>
    <text x="28" y="82">{message}</text>
    <text x="28" y="115" font-size="16">{detail}</text></g>
    <rect x="28" y="140" width="584" height="44" fill="white"/>
    <path d="M28 183V140H611" fill="none" stroke="#808080" stroke-width="2"/>
    <path d="M30 181V142H609" fill="none" stroke="black" stroke-width="2"/>
    <path d="M612 140V184H28" fill="none" stroke="white" stroke-width="2"/>
    <path d="M28 206H612" stroke="#808080"/><path d="M28 207H612" stroke="white"/>
    </svg>'''
    (root/f'{name}.svg').write_text(svg)
    subprocess.run(['magick','-font',font,str(root/f'{name}.svg'),str(root/f'{name}.png')],check=True)
render('unlock', 'Unlock computer', 'Enter your disk password to start Omarchy.', 'Password:')
render('boot', 'Starting Omarchy', 'Please wait while your computer starts.', 'Loading the desktop...')
render('shutdown', 'Shutting down', 'Please wait while your computer shuts down.', 'Saving your session...')
subprocess.run(['magick','-size','8x8','xc:none','-fill','black','-draw','circle 4,4 4,1',str(root/'bullet.png')],check=True)
subprocess.run(['magick','-size','8x34','xc:#000080',str(root/'progress.png')],check=True)
for name in ['unlock','boot','shutdown']:
    args=['magick','-size','1280x800','xc:#008080',str(root/f'{name}.png'),'-geometry','+320+270','-composite']
    if name == 'unlock':
        for i in range(8): args += [str(root/'bullet.png'),'-geometry',f'+{364+i*12}+428','-composite']
    else:
        for i in range(29): args += [str(root/'progress.png'),'-geometry',f'+{353+i*12}+415','-composite']
    subprocess.run(args+[str(root/f'preview-{name}.png')],check=True)
