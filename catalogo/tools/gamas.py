# v2: catálogo completo por gamas, presentación para constructoras, promociones nuevas (sin precios).
import json, os, sys, re, html
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = sys.argv[1]
SEC = json.load(open(f'{BASE}/secciones.json', encoding='utf-8'))
MOD = json.load(open(f'{BASE}/modelos-por-seccion.json', encoding='utf-8'))
PROD = json.load(open(f'{BASE}/productos.json', encoding='utf-8'))
FB, FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f = lambda s, b=True: ImageFont.truetype(FB if b else FR, s)
NAVY, NAVY2, RED, GREY, WHITE, LIGHT = (10, 22, 46), (24, 52, 98), (200, 16, 46), (88, 96, 110), (255, 255, 255), (241, 244, 249)
EMP, TEL = 'AINSHOP TECNOLOGY', '809-437-8927  ·  849-653-8927'
DESC = 'Redes · Cámaras de seguridad · Intercom · Control de acceso · Automatización'
for d in ('paginas', 'promos-gamas', 'promos-v2'): os.makedirs(f'{BASE}/{d}', exist_ok=True)

# ---- 1) páginas por sección (título grande de cada página) y render en alta resolución
doc = pymupdf.open(PDF); pages = {}; cur = None
for pn in range(5, 68):
    t = None
    for b in doc[pn-1].get_text('dict')['blocks']:
        for l in b.get('lines', []):
            s = ''.join(x['text'] for x in l['spans']).strip()
            if l['spans'] and l['spans'][0]['size'] > 22 and re.match(r'\d+\.\d+ ', s): t = t or s
    if t:
        cur = next((k for k in SEC if k.replace(' ', '') == t.replace(' ', '')), None) or next((k for k in SEC if t.startswith(k[:12])), t)
    if cur: pages.setdefault(cur, []).append(pn)
    out = f'{BASE}/paginas/p{pn:02d}.jpg'
    if not os.path.exists(out):
        pix = doc[pn-1].get_pixmap(dpi=170); Image.frombytes('RGB', (pix.width, pix.height), pix.samples).save(out, quality=82)
json.dump(pages, open(f'{BASE}/paginas/secciones-paginas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# ---- utilidades de diseño
def wrap(d, text, fo, w):
    out, cur = [], ''
    for word in text.split():
        t = (cur + ' ' + word).strip()
        if d.textlength(t, font=fo) <= w: cur = t
        else: out.append(cur); cur = word
    return out + ([cur] if cur else [])

def gradient(W, H, c1, c2):
    g = Image.new('RGB', (1, H));
    for y in range(H): g.putpixel((0, y), tuple(int(c1[i] + (c2[i] - c1[i]) * y / H) for i in range(3)))
    return g.resize((W, H))

def white_bg(im):
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); w = Image.new('RGBA', im.size, WHITE + (255,)); w.alpha_composite(im); im = w
    im = im.convert('RGB'); box = ImageChops.difference(im, Image.new('RGB', im.size, WHITE)).getbbox()
    return im.crop(box) if box else im

def fit(im, w, h):
    r = min(w / im.width, h / im.height); im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2)) if r > 1 else im

def promo(img, tag, titulo, sub, puntos, out):
    W, H = 1080, 1350
    c = gradient(W, H, NAVY, NAVY2); d = ImageDraw.Draw(c)
    d.text((60, 62), EMP, font=f(34), fill=WHITE)
    d.text((60, 104), 'Distribuidor e instalador · Santo Domingo, RD', font=f(20, False), fill=(190, 200, 220))
    tw = d.textlength(tag, font=f(26)) + 48
    d.rounded_rectangle([W - 60 - tw, 66, W - 60, 116], 25, fill=RED); d.text((W - 60 - tw / 2, 91), tag, font=f(26), fill=WHITE, anchor='mm')
    y = 160
    for ln in wrap(d, titulo, f(56), W - 120)[:2]: d.text((60, y), ln, font=f(56), fill=WHITE); y += 66
    for ln in wrap(d, sub, f(28, False), W - 120)[:2]: d.text((60, y + 6), ln, font=f(28, False), fill=(205, 214, 230)); y += 36
    top = y + 30; cb = 1000
    d.rounded_rectangle([40, top, W - 40, cb], 28, fill=WHITE)
    im = fit(img, W - 160, cb - top - 60); c.paste(im, ((W - im.width) // 2, top + (cb - top - im.height) // 2))
    yy = cb + 28
    for p in puntos[:3]:
        d.text((60, yy), '✔', font=f(30), fill=(255, 90, 110))
        for i, ln in enumerate(wrap(d, p, f(28, False), W - 170)[:1]): d.text((105, yy + 2), ln, font=f(28, False), fill=WHITE)
        yy += 44
    d.rectangle([0, H - 96, W, H], fill=RED)
    d.text((W // 2, H - 48), 'Cotice por WhatsApp  ' + TEL, font=f(32), fill=WHITE, anchor='mm')
    c.save(out, quality=90)

def page_img(pn):
    im = Image.open(f'{BASE}/paginas/p{pn:02d}.jpg'); return im.crop((0, int(im.height * .13), im.width, im.height))

# ---- 2) promoción por gama: collage de las mejores fotos de la sección (o la página si no hay fotos)
CROPS = sys.argv[2] if len(sys.argv) > 2 else ''
ITEMS = json.load(open(f'{CROPS}/items.json')) if CROPS else []
def collage(k, pns):
    R = globals().get('rows') or []
    ims = [white_bg(Image.open(f"{BASE}/{r['foto']}")) for r in R if r['seccion'] == k and r['foto']][:4]
    if not ims: ims = [white_bg(Image.open(f"{BASE}/{x}")) for x in (globals().get('LINE') or {}).get(k, [])][:4]
    if not ims:
        fs = [i for i in ITEMS if i['seccion'] == k or i['pagina'] in pns]
        ims = [white_bg(Image.open(f"{CROPS}/{i['imagen']}")) for i in fs]
    ims = sorted([x for x in ims if x.width * x.height > 6000], key=lambda x: -x.width * x.height)[:4]
    if not ims: return page_img(pns[0])
    W, H = 1000, 760; c = Image.new('RGB', (W, H), WHITE); n = len(ims)
    cells = [(0, 0, W, H)] if n == 1 else [(0, 0, W // 2, H), (W // 2, 0, W, H)] if n == 2 else \
            [(0, 0, W // 2, H // 2), (W // 2, 0, W, H // 2), (0, H // 2, W, H)] if n == 3 else \
            [(0, 0, W // 2, H // 2), (W // 2, 0, W, H // 2), (0, H // 2, W // 2, H), (W // 2, H // 2, W, H)]
    for im, (a, b, e, g) in zip(ims, cells):
        t = fit(im, e - a - 30, g - b - 30); c.paste(t, (a + (e - a - t.width) // 2, b + (g - b - t.height) // 2))
    return c

for k, pns in pages.items():
    if k not in SEC: continue
    nom, desc, ideal = SEC[k]; code = k.split()[0]
    col = collage(k, pns); os.makedirs(f'{BASE}/img-linea', exist_ok=True); col.save(f'{BASE}/img-linea/{code}-{pns[0]:02d}.jpg', quality=90)
    R = globals().get('rows') or []
    ofi = [r for r in R if r['seccion'] == k and r.get('foto') and r.get('tipo', 'oficial') == 'oficial']
    norm = lambda t: re.sub(r'[^a-z0-9]', '', t.lower())
    for r in R:
        if r['seccion'] != k or r.get('foto'): continue
        best = max(ofi, key=lambda o: len(os.path.commonprefix([norm(o['modelo']), norm(r['modelo'])])), default=None)
        if best and len(os.path.commonprefix([norm(best['modelo']), norm(r['modelo'])])) >= 4:
            r['foto'], r['tipo'] = best['foto'], 'similar'
        elif (globals().get('LINE') or {}).get(k):
            L = LINE[k]; r['foto'], r['tipo'] = L[R.index(r) % len(L)], 'similar'
        else:
            r['foto'], r['tipo'] = f'img-linea/{code}-{pns[0]:02d}.jpg', 'linea'
    promo(col, 'NUEVA LÍNEA', nom, desc, ['Ideal para: ' + ideal, 'Asesoría y levantamiento con nuestros técnicos', 'Instalación profesional · garantía de 90 días en mano de obra'], f'{BASE}/promos-gamas/{code}-{pns[0]:02d}.jpg')

# ---- 3) promociones por producto con el diseño nuevo
for p in PROD:
    promo(white_bg(Image.open(f'{BASE}/{p["img_oficial"]}' if p.get('img_oficial') else f'{BASE}/img/{p["id"]}.png')), 'OFERTA ESPECIAL', p['nombre'], 'Modelo ' + p['modelo'], [p['beneficio'], 'Producto original Hikvision', 'Instalación profesional · garantía de 90 días en mano de obra'], f'{BASE}/promos-v2/{p["id"]}.jpg')

os.makedirs(f'{BASE}/promos-v3', exist_ok=True)
for r in globals().get('rows') or []:
    if not r['foto']: continue
    nom, desc, ideal = SEC.get(r['seccion'], [r['linea'], '', ''])
    sub = 'Modelo ' + r['modelo'] + ('' if r.get('tipo', 'oficial') == 'oficial' else ' · imagen de referencia')
    promo(white_bg(Image.open(f"{BASE}/{r['foto']}")), 'DISPONIBLE', nom, sub, ['Ideal para: ' + ideal, 'Producto original Hikvision', 'Instalación profesional · garantía de 90 días en mano de obra'], f"{BASE}/promos-v3/{r['codigo']}.jpg")

# ---- 4) catálogo completo y presentación para constructoras (HTML -> PDF)
CSS = '''@page{size:A4 landscape;margin:0}body{margin:0;font-family:DejaVu Sans,Arial,sans-serif;color:#0a162e}
.pg{width:297mm;height:210mm;position:relative;page-break-after:always;overflow:hidden;box-sizing:border-box}
.cover{background:linear-gradient(135deg,#0a162e,#183462);color:#fff;padding:38mm 25mm}.cover h1{font-size:46px;margin:0 0 8mm}.cover h2{font-size:26px;font-weight:400;margin:0 0 14mm;color:#cfd8e8}
.pill{display:inline-block;background:#c8102e;color:#fff;border-radius:30px;padding:6px 18px;font-weight:700;font-size:14px}
.bar{position:absolute;left:0;right:0;bottom:0;background:#c8102e;color:#fff;font-weight:700;font-size:15px;padding:9px 14mm}
.head{background:#0a162e;color:#fff;padding:7mm 12mm 6mm}.head h2{margin:0;font-size:24px}.head p{margin:2mm 0 0;font-size:13px;color:#cfd8e8}
.body{display:flex;gap:7mm;padding:6mm 12mm}.body img{width:200mm;border-radius:8px;box-shadow:0 2px 10px #0002}
.side{font-size:11px;line-height:1.45}.side b{color:#c8102e}.side ul{padding-left:14px;margin:2mm 0}
.idx{padding:12mm 16mm;columns:2;font-size:13px;line-height:1.9}.idx b{color:#c8102e;margin-right:6px}
.val{padding:14mm 18mm;display:grid;grid-template-columns:1fr 1fr;gap:9mm}.val div{background:#f1f4f9;border-radius:12px;padding:7mm;font-size:14px}.val h3{margin:0 0 3mm;color:#c8102e}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:5mm;padding:6mm 12mm}.cell{background:#fff;border:1px solid #e3e8f0;border-radius:10px;text-align:center;padding:3mm;height:64mm;display:flex;flex-direction:column;justify-content:space-between}.cell img{height:52mm;object-fit:contain;width:100%}.cell span{font-size:11px;font-weight:700}'''
def sec_pages(keys):
    h = ''
    for k in keys:
        if k not in pages or k not in SEC: continue
        nom, desc, ideal = SEC[k]; mods = MOD.get(k, [])
        R = [r for r in (globals().get('rows') or []) if r['seccion'] == k and r['foto']]
        for j in range(0, len(R), 8):
            cells = ''.join(f'<div class="cell"><img src="{r["foto"]}"><span>{html.escape(r["modelo"])}</span></div>' for r in R[j:j+8])
            h += (f'<div class="pg"><div class="head"><h2>{html.escape(nom)}</h2><p>{html.escape(desc)} · Ideal para: {html.escape(ideal)}</p></div>'
                  f'<div class="grid4">{cells}</div><div class="bar">{EMP} · WhatsApp {TEL} · Precio: solicite su cotización</div></div>')
        for i, pn in enumerate(pages[k]):
            lst = ''.join(f'<li>{html.escape(m)}</li>' for m in mods[:28]) if i == 0 and mods else ''
            h += (f'<div class="pg"><div class="head"><h2>{html.escape(nom)}</h2><p>{html.escape(desc)}</p></div>'
                  f'<div class="body"><img src="paginas/p{pn:02d}.jpg"><div class="side"><b>Ideal para</b><br>{html.escape(ideal)}<br><br>'
                  + (f'<b>Modelos y series</b><ul>{lst}</ul>' if lst else '<b>Modelos</b><br>Ver la imagen: todos los modelos de esta línea están disponibles.') +
                  f'<br><br><b>Precio</b><br>Solicite su cotización.</div></div><div class="bar">{EMP} · WhatsApp {TEL}</div></div>')
    return h
def doc_html(title, sub, keys, extra=''):
    idx = ''.join(f'<div><b>{k.split()[0]}</b>{html.escape(SEC[k][0])}</div>' for k in keys if k in pages)
    return (f'<!doctype html><html lang="es"><meta charset="utf-8"><title>{title}</title><style>{CSS}</style>'
            f'<div class="pg cover"><span class="pill">{EMP}</span><h1 style="margin-top:14mm">{title}</h1><h2>{sub}</h2><p style="font-size:16px">{DESC}<br>Santo Domingo, República Dominicana<br>WhatsApp {TEL}</p></div>'
            f'{extra}<div class="pg"><div class="head"><h2>Índice de líneas de producto</h2><p>Distribuimos e instalamos toda la línea Hikvision</p></div><div class="idx">{idx}</div><div class="bar">Precios: solicite su cotización · Imágenes de referencia del fabricante</div></div>'
            f'{sec_pages(keys)}<div class="pg cover"><h1>¿Hablamos de su proyecto?</h1><h2>Levantamiento técnico, propuesta clara, instalación ordenada y garantía de 90 días en mano de obra.</h2><p style="font-size:26px;font-weight:700">WhatsApp {TEL}</p><p style="font-size:18px">ainshoptecnology.com · Villa Mella, Santo Domingo Norte</p></div></html>')
ALL = list(SEC.keys())
open(f'{BASE}/catalogo-completo.html', 'w', encoding='utf-8').write(doc_html('Catálogo completo Hikvision', 'Todas las líneas de producto que distribuimos e instalamos', ALL))
CONS = ['5.1 Intercom-IP Intercom & 2-Wire', '5.1 Intercom: 4-Wire & SIP & Panic Alarm', '5.2 Access Control-Terminal & Controller & Reader', '5.2 Access Control-Speed Gate & Turnstile',
        '1.1 Channel CCTV', '1.2 Project CCTV', '1.7 Thermal-Security Protection', '3.2 NVR', '3.3 AcuSeek', '5.3 Alarm', '5.4 Fire Alarm-Wired Fire Alarm', '5.5 Vehicle Access Control Management',
        '5.5 Vehicle Access Control Management-License Plate & Long-Range UHF Card', '5.6 Parking Guidance-Indoor Parking Lot', '2.1 Networking-Switch', '2.2 Networking-Wireless Bridge',
        '2.3 Networking-AP & Smart Managed Router', '2.8 PDS', '2.6 Networking-Solar Power Supplement Application', '1.10 Audio', '4.1 LED', '4.4 IFPD-Digital Signage', '6.4 Software- HikCentral Professional']
VAL = ('<div class="pg"><div class="head"><h2>Por qué ainshop tecnology para su obra</h2><p>Un solo proveedor para toda la tecnología del proyecto</p></div><div class="val">'
       '<div><h3>Desde el plano</h3>Diseñamos la seguridad, la red y el intercom junto con su equipo técnico, antes de cerrar paredes.</div>'
       '<div><h3>Todo integrado</h3>Videoportero, control de acceso, cámaras, alarma, incendio, parqueo y red en una sola plataforma (HikCentral / Hik-Connect).</div>'
       '<div><h3>Productos originales</h3>Línea completa Hikvision con soporte del fabricante. Partner registrado (Hik-Partner Pro).</div>'
       '<div><h3>Entrega ordenada</h3>Levantamiento, propuesta clara, instalación limpia, capacitación y garantía de 90 días en mano de obra.</div>'
       '</div><div class="bar">{EMP} · WhatsApp {TEL}</div></div>').replace('{EMP}', EMP).replace('{TEL}', TEL)
open(f'{BASE}/presentacion-constructoras.html', 'w', encoding='utf-8').write(doc_html('Soluciones de seguridad y tecnología para constructoras', 'Residenciales, torres, plazas y proyectos comerciales', CONS, VAL))
print('secciones con páginas:', len(pages), '| promos gamas:', len(os.listdir(f'{BASE}/promos-gamas')), '| promos v2:', len(os.listdir(f'{BASE}/promos-v2')))
if globals().get('rows'):
    json.dump(rows, open(f'{BASE}/productos-v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('modelos con imagen:', sum(1 for r in rows if r.get('foto')), 'de', len(rows))
