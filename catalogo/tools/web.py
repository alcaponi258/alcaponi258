# Sitio web estático del catálogo (buscador por modelo + botón de cotizar por WhatsApp). Sin precios.
import json, os, shutil, html, urllib.parse
from PIL import Image
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f'{BASE}/web'
SEC = json.load(open(f'{BASE}/secciones.json', encoding='utf-8'))
ROWS = json.load(open(f'{BASE}/productos-v3.json', encoding='utf-8'))
PAG = json.load(open(f'{BASE}/paginas/secciones-paginas.json', encoding='utf-8'))
shutil.rmtree(OUT, ignore_errors=True)
for d in ('fotos', 'paginas', 'promos', 'descargas'): os.makedirs(f'{OUT}/{d}')

def webp(src, dst, w):
    im = Image.open(src); im = im.convert('RGBA') if im.mode in ('P', 'LA') else im
    if im.mode == 'RGBA':
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
    im = im.convert('RGB'); im.thumbnail((w, w)); im.save(dst, 'WEBP', quality=82)

items = []
for r in ROWS:
    foto = None
    if r.get('foto'):
        foto = f"fotos/{r['codigo']}.webp"; webp(f"{BASE}/{r['foto']}", f'{OUT}/{foto}', 640)
    pg = PAG.get(r['seccion'], [None])[0]
    items.append({'c': r['codigo'], 'm': r['modelo'], 's': r['seccion'].split()[0], 'l': SEC.get(r['seccion'], [r['linea']])[0],
                  'f': foto, 'p': f'paginas/p{pg:02d}.webp' if pg else None, 'w': r.get('web')})
for pns in PAG.values():
    for pn in pns: webp(f'{BASE}/paginas/p{pn:02d}.jpg', f'{OUT}/paginas/p{pn:02d}.webp', 1600)
for d in ('promos-v3', 'promos-v2', 'promos-gamas'):
    if os.path.isdir(f'{BASE}/{d}'):
        for fn in os.listdir(f'{BASE}/{d}'): shutil.copy(f'{BASE}/{d}/{fn}', f'{OUT}/promos/{fn}')
for fn in ('catalogo-completo.pdf', 'presentacion-constructoras.pdf', 'catalogo-ainshop-hikvision.pdf'):
    if os.path.exists(f'{BASE}/{fn}'): shutil.copy(f'{BASE}/{fn}', f'{OUT}/descargas/{fn}')
secs = [{'s': k.split()[0], 'n': v[0], 'd': v[1], 'i': v[2]} for k, v in SEC.items()]
json.dump({'items': items, 'secciones': secs}, open(f'{OUT}/catalogo.json', 'w', encoding='utf-8'), ensure_ascii=False)
promos = sorted(os.listdir(f'{OUT}/promos'))
json.dump(promos, open(f'{OUT}/promos/lista.json', 'w'))

WA = '18496538927'
page = '''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Catálogo ainshop tecnology · Hikvision</title><meta name="description" content="Catálogo completo Hikvision: cámaras, videoporteros, control de acceso, alarmas, redes. Cotice por WhatsApp. Santo Domingo, RD.">
<style>:root{--n:#0F3460;--r:#EA580C;--g:#5a6270;--bg:#F7F8FA}*{box-sizing:border-box}body{margin:0;font-family:system-ui,Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--n)}
header{background:linear-gradient(135deg,#0F3460,#16467e);color:#fff;padding:22px 16px}header h1{margin:0;font-size:24px}header p{margin:6px 0 0;color:#cfd8e8;font-size:14px}
.bar{position:sticky;top:0;background:#fff;padding:10px 16px;box-shadow:0 2px 8px #0001;display:flex;gap:8px;flex-wrap:wrap;z-index:2}
input,select{font:inherit;padding:10px 12px;border:1px solid #d5dbe5;border-radius:10px;flex:1;min-width:180px}
main{max-width:1200px;margin:0 auto;padding:16px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.card{background:#fff;border-radius:14px;padding:12px;display:flex;flex-direction:column;gap:8px;box-shadow:0 1px 4px #0001}
.card img{width:100%;height:170px;object-fit:contain;background:#fff;cursor:zoom-in}.card small{color:var(--g)}.card b{font-size:15px;word-break:break-word}
.btn{display:block;text-align:center;background:var(--r);color:#fff;text-decoration:none;font-weight:700;border-radius:10px;padding:10px}
.ghost{background:#eef1f6;color:var(--n)}.count{color:var(--g);font-size:14px;margin:4px 0 12px}
.dl{display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 16px}.dl a{background:#fff;border:1px solid #d5dbe5;border-radius:10px;padding:8px 12px;color:var(--n);text-decoration:none;font-size:14px}
dialog{border:0;border-radius:14px;max-width:95vw;padding:0}dialog img{max-width:95vw;max-height:85vh;display:block}
footer{text-align:center;color:var(--g);font-size:13px;padding:24px 16px}.wa{position:fixed;right:16px;bottom:16px;background:#25d366;color:#fff;border-radius:30px;padding:12px 18px;font-weight:700;text-decoration:none;box-shadow:0 4px 12px #0003}</style></head>
<body><header><h1>AINSHOP TECNOLOGY · Catálogo Hikvision</h1><p>Cámaras · Videoporteros · Control de acceso · Alarmas · Incendio · Redes · Pantallas. Santo Domingo, República Dominicana.</p></header>
<div class="bar"><input id="q" placeholder="Busque por modelo o equipo (ej. DS-2CD2347, videoportero, térmica)" autofocus><select id="sec"><option value="">Todas las líneas</option></select></div>
<main><div class="dl"><a href="descargas/catalogo-completo.pdf">📘 Catálogo completo (PDF)</a><a href="descargas/presentacion-constructoras.pdf">🏗️ Presentación para constructoras (PDF)</a></div>
<div class="count" id="count"></div><div class="grid" id="grid"></div></main>
<dialog id="dlg" onclick="this.close()"><img id="big" alt=""></dialog>
<footer>Precios y disponibilidad: solicite su cotización. Instalación profesional y garantía de 90 días en mano de obra. Imágenes de referencia del fabricante.</footer>
<a class="wa" href="https://wa.me/__WA__?text=Hola%2C%20quiero%20una%20cotizaci%C3%B3n">WhatsApp</a>
<script>
const WA="__WA__";let D;
fetch("catalogo.json").then(r=>r.json()).then(j=>{D=j;const s=document.getElementById("sec");
j.secciones.forEach(x=>{if(j.items.some(i=>i.s==x.s)){const o=document.createElement("option");o.value=x.s;o.textContent=x.n;s.appendChild(o)}});
const p=new URLSearchParams(location.search);if(p.get("q"))q.value=p.get("q");if(p.get("linea"))s.value=p.get("linea");draw()});
const norm=t=>(t||"").toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").replace(/[^a-z0-9]/g,"");
function draw(){const t=norm(q.value),s=sec.value;const g=document.getElementById("grid");
const L=D.items.filter(i=>(!s||i.s==s)&&(!t||norm(i.m+i.l+i.c).includes(t)||norm(i.m).includes(t.replace(/x/g,""))));
count.textContent=L.length+" equipos";g.innerHTML=L.slice(0,400).map(i=>{const img=i.f||i.p;const msg=encodeURIComponent("Hola, quiero cotizar: "+i.m+" ("+i.c+")");
return `<div class="card">${img?`<img loading="lazy" src="${img}" alt="${i.m}" onclick="big.src='${img}';dlg.showModal()">`:""}<small>${i.l}</small><b>${i.m}</b><small>Código ${i.c}</small>
<a class="btn" href="https://wa.me/${WA}?text=${msg}">Cotizar por WhatsApp</a>${i.w?`<a class="btn ghost" href="${i.w}" target="_blank" rel="noopener">Ficha técnica</a>`:""}</div>`}).join("")}
q.oninput=draw;sec.onchange=draw;
</script></body></html>'''.replace('__WA__', WA)
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(page)
open(f'{OUT}/_headers', 'w').write('/promos/*\n  Access-Control-Allow-Origin: *\n/catalogo.json\n  Access-Control-Allow-Origin: *\n')
print('modelos en la web:', len(items), '· con foto:', sum(1 for i in items if i['f']), '· promos:', len(promos))

# Hoja para Meta Commerce Manager (columnas del documento de Marco). Precio vacío: lo completa Marco.
import csv
BASE_URL = os.environ.get('CATALOGO_URL', 'https://CAMBIAR-POR-LA-DIRECCION-DE-LA-WEB')
with open(f'{BASE}/meta-catalogo.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['id', 'title', 'description', 'availability', 'condition', 'price', 'link', 'image_link', 'brand', 'sale_price'])
    for r in ROWS:
        nom, desc, ideal = SEC.get(r['seccion'], [r['linea'], '', ''])
        w.writerow([r['codigo'], f"{nom} Hikvision {r['modelo']}"[:150], f"{desc} Ideal para: {ideal}. Instalación profesional en Santo Domingo. Cotice por WhatsApp 849-653-8927.",
                    'in stock', 'new', '', 'https://wa.me/18496538927', f"{BASE_URL}/promos/{r['codigo']}.jpg", 'Hikvision', ''])
print('meta-catalogo.csv:', len(ROWS), 'filas')
