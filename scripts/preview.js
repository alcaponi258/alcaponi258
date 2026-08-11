import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { marked } from "marked";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(__dirname, "..");
const readmePath = join(repoRoot, "README.md");

const PORT = Number(process.env.PORT) || 3000;
const HOST = process.env.HOST || "0.0.0.0";

function page(bodyHtml) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>alcaponi258 · README preview</title>
<style>
  :root { color-scheme: light dark; }
  body {
    margin: 0;
    background: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    display: flex;
    justify-content: center;
    padding: 32px 16px;
  }
  .readme {
    width: 100%;
    max-width: 860px;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 32px 40px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }
  .readme h1, .readme h2 { border-bottom: 1px solid #30363d; padding-bottom: .3em; }
  .readme a { color: #58a6ff; }
  .readme code { background: #30363d; padding: .2em .4em; border-radius: 6px; }
  .readme pre { background: #0d1117; padding: 16px; border-radius: 8px; overflow: auto; }
  .banner { max-width: 860px; width: 100%; margin: 0 auto 12px; color: #8b949e; font-size: 13px; }
</style>
</head>
<body>
<div>
  <div class="banner">Local preview of <code>README.md</code> — served by the dev environment</div>
  <article class="readme">
    ${bodyHtml}
  </article>
</div>
</body>
</html>`;
}

const server = createServer(async (req, res) => {
  if (req.url === "/healthz") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ ok: true }));
    return;
  }
  try {
    const md = await readFile(readmePath, "utf8");
    const html = marked.parse(md);
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    res.end(page(html));
  } catch (err) {
    res.writeHead(500, { "content-type": "text/plain" });
    res.end(`Failed to render README.md: ${err.message}`);
  }
});

server.listen(PORT, HOST, () => {
  console.log(`README preview running at http://${HOST}:${PORT}`);
});
