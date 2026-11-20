# Extrae fotos de producto del catálogo Hikvision, agrupadas por la etiqueta de modelo más cercana.
import pymupdf, re, json, sys, os
pdf, out = sys.argv[1], sys.argv[2]
PAGES = [p for p in range(5, 68)]
os.makedirs(out, exist_ok=True)
d = pymupdf.open(pdf); items = []
clean = pymupdf.open(pdf)   # copia sin texto para recortar fotos limpias
for pn in PAGES:
    cp = clean[pn-1]
    for b in cp.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s_ in l['spans']: cp.add_redact_annot(s_['bbox'], fill=False)
    cp.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE); seen=set()
MODEL = re.compile(r'(DS-|[A-Z]{1,4}[0-9]{2,}|[Ss]eries|Kit|Solar|4G|Panoramic|Fisheye|Explosion|Anti-corrosion|DeepinView|Turnstile|Speed Gate|Panel|Station|Router|Switch|UPS|Monitor|Cabinet|Bridge|Panic|Peripherals|Distributor|Barrier|Reader|Terminal|Controller)')
SKIP = re.compile(r'^(\||IP\d|\d+$|[❶-❿➊-➓]|Network Camera|Turbo HD|Channel|NVR$|Flexible|Support|Local GUI)')
SEC = {}
for pn in PAGES:
    m = re.search(r'^\s*(\d+\.\d+)\s+(.+)$', d[pn-1].get_text(), re.M)
    if m: SEC[pn] = m.group(1) + ' ' + m.group(2).strip()
for pn in PAGES:
    pg = d[pn-1]
    imgs = []
    for i in pg.get_image_info(xrefs=True):
        nat = i.get('width', 0) / max(1, i['bbox'][2]-i['bbox'][0]) * 72
        x0,y0,x1,y1 = i['bbox']; w,h = x1-x0, y1-y0
        if y0 < 70 or w < 14 or h < 14: continue           # cabecera/QR/logo
        if w/h > 2.2 or h/w > 3.5: continue                 # insignias tipo logo
        if w*h > 960*540*0.25: continue                     # fondos
        imgs.append((x0,y0,x1,y1,max(300, min(900, nat))))
    labels = []
    for b in pg.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            t = ' '.join(s['text'].strip() for s in l['spans']).strip()
            sz = max(s['size'] for s in l['spans'])
            if 7.5 <= sz <= 11 and MODEL.search(t) and not t.endswith('.') and len(t) < 45 and not SKIP.match(t):
                labels.append((t, l['bbox']))
    for t,(lx0,ly0,lx1,ly1) in labels:
        best = None
        for side in ('below','above'):
            sel = []
            for (x0,y0,x1,y1,xr) in imgs:
                cx = (x0+x1)/2
                if not (lx0-35 <= cx <= lx1+35): continue
                if side=='below' and ly1-3 <= y0 <= ly1+95: sel.append((x0,y0,x1,y1,xr))
                if side=='above' and ly0-95 <= y1 <= ly0+3: sel.append((x0,y0,x1,y1,xr))
            area = sum((b[2]-b[0])*(b[3]-b[1]) for b in sel)
            if sel and (best is None or area > best[0]): best = (area, sel)
        if not best: continue
        sel = best[1]
        big = max(sel, key=lambda b:(b[2]-b[0])*(b[3]-b[1]))
        key=(pn,t)
        if key in seen: continue
        seen.add(key)
        fn = f"p{pn:02d}_{re.sub(r'[^A-Za-z0-9]+','_',t)[:40]}.png"
        r = pymupdf.Rect(big[:4]) + (-1, -1, 1, 1)
        clean[pn-1].get_pixmap(clip=r, dpi=int(big[4])).save(os.path.join(out, fn))
        items.append({'pagina': pn, 'modelo': t, 'imagen': fn, 'seccion': SEC.get(pn, '')})
json.dump(items, open(os.path.join(out,'items.json'),'w'), ensure_ascii=False, indent=1)
print(len(items))
