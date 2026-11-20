# Comerciales verticales 1080x1920: diapositivas con diseño v2 + movimiento + transiciones + voz (si existe).
# Uso: comercial.py [carpeta_voces]   (voz-camaras.mp3, voz-redes.mp3, voz-intercom.mp3, voz-acceso.mp3)
import json, os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOZ = sys.argv[1] if len(sys.argv) > 1 else ''
P = json.load(open(f'{BASE}/productos.json', encoding='utf-8'))
FB, FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f = lambda s, b=True: ImageFont.truetype(FB if b else FR, s)
NAVY, NAVY2, RED, WHITE = (10, 22, 46), (24, 52, 98), (200, 16, 46), (255, 255, 255)
W, H = 1080, 1920
REELS = {'camaras': ('Cámaras de seguridad', 'que te avisan al celular', ['Cámaras IP', 'Cámaras sin cable', 'Kits', 'Cámaras Turbo HD', 'Cámaras de proyecto'], ['1.1', '1.2', '1.7']),
         'redes': ('Grabadores, redes', 'y energía sin cortes', ['Grabadores NVR', 'Redes', 'Energía'], ['2.1', '2.2', '2.8']),
         'intercom': ('Videoporteros', 'para casas y edificios', ['Intercom'], ['5.1']),
         'acceso': ('Control de acceso', 'y alarmas inteligentes', ['Control de acceso', 'Control vehicular', 'Alarmas'], ['5.2', '5.3', '5.4', '5.5'])}

def grad():
    g = Image.new('RGB', (1, H))
    for y in range(H): g.putpixel((0, y), tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * y / H) for i in range(3)))
    return g.resize((W, H))
def wrap(d, t, fo, w):
    out, cur = [], ''
    for x in t.split():
        s = (cur + ' ' + x).strip()
        if d.textlength(s, font=fo) <= w: cur = s
        else: out.append(cur); cur = x
    return out + ([cur] if cur else [])
def fit(im, w, h):
    r = min(w / im.width, h / im.height); im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(2, 70, 2)) if r > 1 else im
def clean(im):
    im = im.convert('RGB'); b = ImageChops.difference(im, Image.new('RGB', im.size, WHITE)).getbbox(); return im.crop(b) if b else im
def brand(d):
    d.text((70, 90), 'AINSHOP TECNOLOGY', font=f(44), fill=WHITE)
    d.rectangle([70, 150, 230, 156], fill=RED)
def slide_cover(t1, t2):
    c = grad(); d = ImageDraw.Draw(c); brand(d)
    d.text((70, 720), t1, font=f(92), fill=WHITE); d.text((70, 830), t2, font=f(60, False), fill=(205, 214, 230))
    d.rounded_rectangle([70, 960, 560, 1040], 40, fill=RED); d.text((315, 1000), 'Original Hikvision', font=f(38), fill=WHITE, anchor='mm')
    return c
def slide_img(tag, title, line, im):
    c = grad(); d = ImageDraw.Draw(c); brand(d)
    d.text((70, 250), tag.upper(), font=f(36), fill=(255, 110, 130)); y = 305
    for ln in wrap(d, title, f(76), W - 140)[:2]: d.text((70, y), ln, font=f(76), fill=WHITE); y += 90
    d.rounded_rectangle([50, 540, W - 50, 1460], 40, fill=WHITE)
    t = fit(im, W - 200, 820); c.paste(t, ((W - t.width) // 2, 540 + (920 - t.height) // 2))
    y = 1520
    for ln in wrap(d, line, f(46, False), W - 140)[:3]: d.text((70, y), ln, font=f(46, False), fill=WHITE); y += 60
    return c
def slide_cta():
    c = Image.new('RGB', (W, H), RED); d = ImageDraw.Draw(c)
    d.text((W // 2, 640), 'Cotiza hoy', font=f(110), fill=WHITE, anchor='mm')
    d.text((W // 2, 760), 'por WhatsApp', font=f(64, False), fill=WHITE, anchor='mm')
    for i, n in enumerate(['809-437-8927', '849-653-8927']):
        d.rounded_rectangle([140, 880 + i * 170, W - 140, 1010 + i * 170], 60, fill=WHITE)
        d.text((W // 2, 945 + i * 170), n, font=f(84), fill=RED, anchor='mm')
    d.text((W // 2, 1340), 'Instalación profesional · Garantía', font=f(44, False), fill=WHITE, anchor='mm')
    d.text((W // 2, 1440), 'AINSHOP TECNOLOGY', font=f(56), fill=WHITE, anchor='mm')
    return c

def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout or 0)

os.makedirs(f'{BASE}/comerciales', exist_ok=True)
for key, (t1, t2, cats, gamas) in REELS.items():
    out = f'{BASE}/comerciales/{key}'; os.makedirs(out, exist_ok=True)
    sl = [slide_cover(t1, t2)]
    for p in [x for x in P if x['cat'] in cats][:7]:
        sl.append(slide_img(p['cat'], p['nombre'], p['beneficio'], clean(Image.open(f'{BASE}/{p["img_oficial"]}' if p.get('img_oficial') else f'{BASE}/img/{p["id"]}.png'))))
    for g in gamas:
        fs = sorted(x for x in os.listdir(f'{BASE}/promos-gamas') if x.startswith(g + '-'))[:1]
        for fn in fs:
            im = Image.open(f'{BASE}/promos-gamas/{fn}').crop((40, 300, 1040, 1000))
            sl.append(slide_img('Toda la línea', 'Y mucho más', 'Pregunte por toda la línea disponible para su proyecto.', im))
    sl.append(slide_cta())
    for i, s in enumerate(sl): s.save(f'{out}/{i:02d}.jpg', quality=90)
    voz = os.path.join(VOZ, f'voz-{key}.mp3') if VOZ else ''
    total = max(dur(voz) + 1.5, 4.0 * len(sl)) if voz and os.path.exists(voz) else 4.0 * len(sl)
    n, X = len(sl), 0.5; d = (total + X * (n - 1)) / n
    inp, flt = [], []
    for i in range(n):
        inp += ['-loop', '1', '-t', f'{d:.2f}', '-i', f'{out}/{i:02d}.jpg']
        z = 'min(zoom+0.0006,1.06)' if i % 2 == 0 else 'if(eq(on,1),1.06,max(zoom-0.0006,1))'
        flt.append(f'[{i}:v]scale=1188:2112,zoompan=z=\'{z}\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={int(d*30)}:s={W}x{H}:fps=30,setsar=1[v{i}]')
    prev, off = 'v0', 0.0
    for i in range(1, n):
        off += d - X; flt.append(f'[{prev}][v{i}]xfade=transition={"slideleft" if i % 2 else "fade"}:duration={X}:offset={off:.2f}[x{i}]'); prev = f'x{i}'
    cmd = ['ffmpeg', '-loglevel', 'error', '-y'] + inp
    if voz and os.path.exists(voz): cmd += ['-i', voz]
    cmd += ['-filter_complex', ';'.join(flt), '-map', f'[{prev}]']
    if voz and os.path.exists(voz): cmd += ['-map', f'{n}:a', '-c:a', 'aac', '-b:a', '128k', '-af', 'adelay=600|600,apad', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{BASE}/comerciales/comercial-{key}.mp4']
    subprocess.run(cmd, check=True)
    print(key, n, 'diapositivas', round(total, 1), 's', 'con voz' if voz and os.path.exists(voz) else 'sin voz')
