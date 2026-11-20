# v3: une las fotos oficiales de hikvision.com con todos los modelos del PDF.
# Produce: productos-v3.json, img-oficial/, promos-v3/ (1 por modelo con foto), promos-gamas/ (collage oficial),
#          scgv-inventario.csv (TODOS los modelos), catálogo y presentación con cuadrícula de fotos oficiales.
import json, os, re, sys, shutil, csv
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HV = sys.argv[1]                                   # carpeta con map.json y fotos oficiales
sys.argv = [sys.argv[0], sys.argv[2], sys.argv[3]]  # gamas.py espera: pdf, crops
SEC = json.load(open(f'{BASE}/secciones.json', encoding='utf-8'))
MOD = json.load(open(f'{BASE}/modelos-por-seccion.json', encoding='utf-8'))
MAP = json.load(open(f'{HV}/map.json'))
PROD = json.load(open(f'{BASE}/productos.json', encoding='utf-8'))
os.makedirs(f'{BASE}/img-oficial', exist_ok=True)

def tokens(n):
    return [t.strip(' -') for t in re.split(r'\s*/\s*|\s*,\s*', re.sub(r'\s+(series|Series)$', '', n))]

# 1) todos los modelos, con su sección y su foto oficial si existe
rows, seen = [], set()
for sec, mods in MOD.items():
    for m in mods:
        if m in seen: continue
        seen.add(m)
        foto = next((MAP[t]['file'] for t in tokens(m) if t in MAP and MAP[t].get('file')), None)
        url = next((MAP[t]['url'] for t in tokens(m) if t in MAP and MAP[t].get('url')), None)
        if foto: shutil.copy(f'{HV}/{foto}', f'{BASE}/img-oficial/{foto}')
        rows.append({'modelo': m, 'seccion': sec, 'linea': SEC.get(sec, [sec])[0], 'foto': foto and f'img-oficial/{foto}', 'web': url})
# secciones sin modelos escritos: se listan como línea completa
for sec in SEC:
    if not any(r['seccion'] == sec for r in rows):
        rows.append({'modelo': 'Línea completa (ver catálogo)', 'seccion': sec, 'linea': SEC[sec][0], 'foto': None, 'web': None})
for i, r in enumerate(rows): r['codigo'] = f'HK-{i+1:03d}'
json.dump(rows, open(f'{BASE}/productos-v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# 2) los 36 productos destacados usan la foto oficial cuando existe
for p in PROD:
    f = next((MAP[t]['file'] for t in tokens(p['modelo']) if t in MAP and MAP[t].get('file')), None)
    if f: p['img_oficial'] = f'img-oficial/{f}'; shutil.copy(f'{HV}/{f}', f'{BASE}/img-oficial/{f}')
json.dump(PROD, open(f'{BASE}/productos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# 3) inventario SCGV con TODOS los modelos (sin precio)
with open(f'{BASE}/scgv-inventario.csv', 'w', newline='', encoding='utf-8-sig') as fh:
    w = csv.writer(fh); w.writerow(['codigo', 'nombre', 'modelo', 'marca', 'categoria', 'descripcion', 'imagen', 'precio', 'existencia'])
    for r in rows:
        nom, desc, ideal = SEC.get(r['seccion'], [r['linea'], '', ''])
        w.writerow([r['codigo'], f"{nom} {r['modelo']}", r['modelo'], 'Hikvision', nom, f'{desc} Ideal para: {ideal}.', r['foto'] or '', '', 0])
con = sum(1 for r in rows if r['foto'])
print(f'modelos: {len(rows)} · con foto oficial: {con} · secciones: {len(SEC)}')

# fotos oficiales por línea (categorías de hikvision.com) para líneas sin foto por modelo
LINE = {}
for k, v in MAP.items():
    if k.startswith('SEC::') and v.get('file'):
        sec = k.split('::')[1]; shutil.copy(f'{HV}/{v["file"]}', f'{BASE}/img-oficial/{v["file"]}')
        LINE.setdefault(sec, []).append(f'img-oficial/{v["file"]}')

# 4) reusar el generador de gamas con las fotos oficiales
exec(open(f'{BASE}/tools/gamas.py', encoding='utf-8').read().replace('#__V3__', ''))
