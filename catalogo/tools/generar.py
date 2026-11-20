# Genera catálogo, promociones, slides de reels, inventario SCGV y lista para el Puente (sin precios).
import json, os, sys, shutil, csv, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageChops

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROPS = sys.argv[1]
P = json.load(open(os.path.join(BASE, 'productos.json'), encoding='utf-8'))
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'
def font(sz, b=True): return ImageFont.truetype(F % ('-Bold' if b else ''), sz)
NAVY, RED, GREY, WHITE = (13, 27, 52), (200, 16, 46), (90, 98, 112), (255, 255, 255)
EMPRESA = "AINSHOP TECNOLOGY"
DESC = "Redes · Cámaras de seguridad · Intercom · Control de acceso · Automatización"
TEL = "WhatsApp 809-437-8927 · 849-653-8927"
for d in ('img', 'promos', 'reels'): os.makedirs(os.path.join(BASE, d), exist_ok=True)

def trim(im):
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); w = Image.new('RGBA', im.size, (255, 255, 255, 255)); w.alpha_composite(im); im = w
    im = im.convert('RGB'); bg = Image.new('RGB', im.size, WHITE)
    box = ImageChops.difference(im, bg).getbbox()
    return im.crop(box) if box else im

def fit(im, w, h):
    r = min(w / im.width, h / im.height); return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def wrap(draw, text, f, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=f) <= width: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur] if cur else lines

def header_footer(d, W, H, top=90):
    d.rectangle([0, 0, W, top], fill=NAVY)
    d.text((40, top // 2), EMPRESA, font=font(int(top * .42)), fill=WHITE, anchor='lm')
    d.rectangle([0, H - 150, W, H], fill=NAVY)
    d.text((W // 2, H - 105), DESC, font=font(26, False), fill=WHITE, anchor='mm')
    d.text((W // 2, H - 55), TEL, font=font(34), fill=WHITE, anchor='mm')

# 1) imágenes limpias
for p in P:
    im = Image.open(os.path.join(CROPS, p['img']))
    if p.get('recorte_inferior'): im = im.crop((0, 0, im.width, int(im.height * (1 - p['recorte_inferior']))))
    im = trim(im)
    im.save(os.path.join(BASE, 'img', p['id'] + '.png'))

# 2) promociones 1080x1080 (sin precio) + textos para WhatsApp
cap = []
for p in P:
    W = H = 1080; c = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(c)
    header_footer(d, W, H)
    d.rounded_rectangle([40, 115, 330, 165], 12, fill=RED)
    d.text((185, 140), 'OFERTA ESPECIAL', font=font(26), fill=WHITE, anchor='mm')
    d.text((W - 40, 140), p['cat'].upper(), font=font(24), fill=GREY, anchor='rm')
    y = 190
    for ln in wrap(d, p['nombre'], font(52), W - 80): d.text((40, y), ln, font=font(52), fill=NAVY); y += 62
    d.text((40, y + 4), 'Modelo: ' + p['modelo'], font=font(28, False), fill=GREY); y += 50
    im = fit(Image.open(os.path.join(BASE, 'img', p['id'] + '.png')), W - 160, 900 - y - 150)
    c.paste(im, ((W - im.width) // 2, y + (900 - y - 150 - im.height) // 2))
    yy = 760
    for ln in wrap(d, '✔ ' + p['beneficio'], font(32), W - 80)[:2]: d.text((40, yy), ln, font=font(32), fill=NAVY); yy += 40
    d.text((40, yy + 6), 'Pida su cotización por WhatsApp · Instalación y garantía de 90 días en mano de obra', font=font(22, False), fill=GREY)
    c.save(os.path.join(BASE, 'promos', p['id'] + '.jpg'), quality=88)
    cap.append(f"[{p['id']}] {p['nombre']} ({p['modelo']})\n{p['que']} {p['beneficio']}\n"
               f"ainshop tecnology, empresa de tecnología en Santo Domingo, República Dominicana: redes, cámaras de seguridad Hikvision, intercom, control de acceso y automatizaciones. Tel. 809-437-8927.\n"
               f"Escríbanos y le enviamos su cotización.\n")
open(os.path.join(BASE, 'promos', 'textos-whatsapp.txt'), 'w', encoding='utf-8').write('\n'.join(cap))

# 3) slides de reels 1080x1920 por grupo + portada/cierre
GRUPOS = {'reel-camaras': ['Cámaras IP', 'Cámaras sin cable', 'Kits', 'Cámaras Turbo HD', 'Cámaras de proyecto'],
          'reel-grabadores-redes': ['Grabadores NVR', 'Redes', 'Energía'],
          'reel-intercom': ['Intercom'],
          'reel-acceso-alarmas': ['Control de acceso', 'Control vehicular', 'Alarmas']}
TIT = {'reel-camaras': 'Cámaras de seguridad Hikvision', 'reel-grabadores-redes': 'Grabación, redes y energía',
       'reel-intercom': 'Videoporteros e intercom', 'reel-acceso-alarmas': 'Control de acceso y alarmas'}
for g, cats in GRUPOS.items():
    out = os.path.join(BASE, 'reels', g); os.makedirs(out, exist_ok=True)
    W, H = 1080, 1920; n = 0
    def slide(): c = Image.new('RGB', (W, H), WHITE); return c, ImageDraw.Draw(c)
    c, d = slide(); c.paste(NAVY, [0, 0, W, H])
    d.text((W // 2, 760), EMPRESA, font=font(70), fill=WHITE, anchor='mm')
    yy = 900
    for ln in wrap(d, TIT[g], font(64), W - 120): d.text((W // 2, yy), ln, font=font(64), fill=WHITE, anchor='mm'); yy += 80
    d.text((W // 2, yy + 60), 'Instalación profesional en el Gran Santo Domingo', font=font(36, False), fill=WHITE, anchor='mm')
    c.save(f'{out}/{n:02d}.jpg', quality=88); n += 1
    for p in [x for x in P if x['cat'] in cats]:
        c, d = slide(); header_footer(d, W, H, 130)
        d.text((60, 200), p['cat'].upper(), font=font(34), fill=RED)
        y = 260
        for ln in wrap(d, p['nombre'], font(70), W - 120): d.text((60, y), ln, font=font(70), fill=NAVY); y += 82
        d.text((60, y + 10), p['modelo'], font=font(34, False), fill=GREY)
        im = fit(Image.open(os.path.join(BASE, 'img', p['id'] + '.png')), W - 120, 760)
        c.paste(im, ((W - im.width) // 2, 560 + (760 - im.height) // 2))
        yy = 1380
        for ln in wrap(d, '✔ ' + p['beneficio'], font(44), W - 120)[:3]: d.text((60, yy), ln, font=font(44), fill=NAVY); yy += 56
        c.save(f'{out}/{n:02d}.jpg', quality=88); n += 1
    c, d = slide(); c.paste(RED, [0, 0, W, H])
    d.text((W // 2, 800), 'Pida su cotización', font=font(80), fill=WHITE, anchor='mm')
    d.text((W // 2, 920), 'por WhatsApp', font=font(64, False), fill=WHITE, anchor='mm')
    d.text((W // 2, 1060), '809-437-8927', font=font(90), fill=WHITE, anchor='mm')
    d.text((W // 2, 1180), '849-653-8927', font=font(90), fill=WHITE, anchor='mm')
    d.text((W // 2, 1340), EMPRESA, font=font(48), fill=WHITE, anchor='mm')
    c.save(f'{out}/{n:02d}.jpg', quality=88)

# 4) inventario para el SCGV (sin precio)
with open(os.path.join(BASE, 'scgv-inventario.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['codigo', 'nombre', 'modelo', 'marca', 'categoria', 'descripcion', 'imagen', 'precio', 'existencia'])
    for p in P: w.writerow([p['id'], p['nombre'], p['modelo'], 'Hikvision', p['cat'], p['que'] + ' ' + p['beneficio'], f"img/{p['id']}.png", '', 0])

# 5) lista compacta para el Puente
lines = ['CATÁLOGO AINSHOP (Hikvision, sin precios: el precio siempre lo confirma Marco). Código · producto · modelo']
cat = None
for p in P:
    if p['cat'] != cat: cat = p['cat']; lines.append(f'- {cat}:')
    lines.append(f"  {p['id']} · {p['nombre']} · {p['modelo']}")
open(os.path.join(BASE, 'lista-puente.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# 6) catálogo HTML (para PDF)
cards = ''
for cat in dict.fromkeys(x['cat'] for x in P):
    cards += f'<h2>{cat}</h2><div class="grid">'
    for p in [x for x in P if x['cat'] == cat]:
        cards += (f'<div class="card"><img src="img/{p["id"]}.png"><div><b>{p["nombre"]}</b><small>{p["id"]} · {p["modelo"]}</small>'
                  f'<p>{p["que"]}</p><p class="b">✔ {p["beneficio"]}</p></div></div>')
    cards += '</div>'
html = f'''<!doctype html><html lang="es"><meta charset="utf-8"><title>Catálogo ainshop</title><style>
@page{{size:A4;margin:12mm}}body{{font-family:Liberation Sans,Arial,sans-serif;color:#0d1b34;margin:0}}
.cover{{height:265mm;background:#0d1b34;color:#fff;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;page-break-after:always}}
.cover h1{{font-size:44px;margin:0}}.cover p{{font-size:20px;max-width:150mm}}
h2{{background:#c8102e;color:#fff;padding:6px 10px;font-size:18px;margin:14px 0 8px;break-after:avoid}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}.card{{display:flex;gap:10px;border:1px solid #dde;border-radius:8px;padding:8px;break-inside:avoid}}
.card img{{width:38mm;height:30mm;object-fit:contain}}.card b{{display:block;font-size:13px}}small{{color:#5a6270;font-size:10px}}
.card p{{font-size:10.5px;margin:4px 0}}.b{{color:#c8102e}}footer{{margin-top:12px;font-size:11px;text-align:center;color:#5a6270}}
</style><div class="cover"><h1>{EMPRESA}</h1><p>Catálogo de productos Hikvision<br>{DESC}</p><p>Santo Domingo, República Dominicana<br>{TEL}</p></div>
{cards}<footer>Precios y disponibilidad: solicite su cotización. Instalación profesional y garantía de 90 días en mano de obra. Imágenes de referencia del fabricante.</footer></html>'''
open(os.path.join(BASE, 'catalogo.html'), 'w', encoding='utf-8').write(html)
print('ok', len(P))
