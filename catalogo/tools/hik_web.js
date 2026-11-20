// Busca cada modelo/serie del catálogo en hikvision.com (sitemap) y baja la foto oficial (1280px).
// Uso: node hik_web.js modelos.json prod_urls.txt carpeta_salida
const {chromium} = require('playwright'); const fs = require('fs'); const path = require('path');
const [modelsFile, urlsFile, out] = process.argv.slice(2);
fs.mkdirSync(out, {recursive: true});
const urls = fs.readFileSync(urlsFile, 'utf8').split('\n').filter(Boolean);
const models = JSON.parse(fs.readFileSync(modelsFile, 'utf8'));   // [{key, pattern}]
const mapFile = path.join(out, 'map.json');
const map = fs.existsSync(mapFile) ? JSON.parse(fs.readFileSync(mapFile)) : {};
function pick(pat) {
  const re = new RegExp(pat, 'i');
  const m = urls.filter(u => re.test(u.split('/').slice(-2, -1)[0] || ''));
  return m.sort((a, b) => a.length - b.length)[0];
}
(async () => {
  const px = process.env.HTTPS_PROXY;
  const b = await chromium.launch({proxy: px ? {server: px} : undefined});
  const c = await b.newContext({userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'});
  const p = await c.newPage();
  await p.goto('https://www.hikvision.com/en/', {waitUntil: 'load', timeout: 60000}); await p.waitForTimeout(2500);
  for (const {key, pattern} of models) {
    if (map[key] && map[key].file) continue;
    const u = pick(pattern); if (!u) { map[key] = {url: null}; continue; }
    try {
      await p.goto(u, {waitUntil: 'domcontentloaded', timeout: 45000});
      let img = await p.$eval('meta[name="page-image"]', m => m.content).catch(() => null);
      if (!img) { await p.waitForTimeout(1500); await p.goto(u, {waitUntil: 'domcontentloaded', timeout: 45000}); img = await p.$eval('meta[name="page-image"]', m => m.content).catch(() => null); }
      if (!img) { map[key] = {url: u, img: null}; continue; }
      const r = await c.request.get(encodeURI(decodeURI(img)));
      const ext = (img.match(/\.(png|jpe?g|webp)$/i) || ['.png'])[0];
      const file = key.replace(/[^A-Za-z0-9]+/g, '_').slice(0, 50) + ext;
      if (r.ok()) { fs.writeFileSync(path.join(out, file), await r.body()); map[key] = {url: u, img, file}; }
      else map[key] = {url: u, img, status: r.status()};
    } catch (e) { map[key] = {url: u, error: e.message.slice(0, 80)}; }
    fs.writeFileSync(mapFile, JSON.stringify(map, null, 1));
    process.stdout.write('.');
  }
  await b.close();
  const ok = Object.values(map).filter(v => v.file).length;
  console.log(`\n${ok} fotos de ${models.length} modelos`);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
