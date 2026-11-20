# Lista todos los modelos/series escritos en cada página del catálogo, agrupados por sección.
import pymupdf, re, json, sys
d = pymupdf.open(sys.argv[1]); out = {}
PAT = re.compile(r'(DS-[A-Z0-9][A-Za-z0-9()/+\-]{3,}|i?DS-\w+|\b[A-Z]{1,4}\d{2,}[A-Za-z0-9()/\-]*(?:\s(?:series|Series))?|\b[A-Z][A-Za-z0-9+\-]*(?:\s[A-Z0-9][A-Za-z0-9+\-]*){0,2}\s(?:series|Series)\b|HikCentral[\w \-]*|Hik-Connect|Hik-Partner Pro|AX (?:PRO|HOME|Hybrid PRO)|DeepinMind[\w ]*|AcuSeek[\w ]*|ColorVu[\w .]*|TandemVu|DeepinView\w*)')
sec = ''
for pn in range(5, 68):
    t = d[pn-1].get_text()
    m = re.search(r'^\s*(\d+\.\d+)\s+(.+)$', t, re.M)
    if m: sec = m.group(1) + ' ' + m.group(2).strip()
    found = []
    for x in PAT.findall(t.replace('\n', ' ')):
        x = re.sub(r'\s+', ' ', x).strip(' -/')
        if len(x) >= 3 and not re.fullmatch(r'[A-Z]{1,2}\d{2,3}', x) and x not in found: found.append(x)
    out.setdefault(sec, [])
    for f in found:
        if f not in out[sec]: out[sec].append(f)
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
print(sum(len(v) for v in out.values()), 'modelos en', len(out), 'secciones')
for k, v in out.items(): print(f'{len(v):3d} {k[:55]}')
