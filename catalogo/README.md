# Catálogo ainshop (Hikvision, sin precios)

Fuente: HIKVISION Product Catalog 2026H2 (V1.4). 36 productos con foto + 4 sin foto.

- `catalogo-ainshop-hikvision.pdf`: catálogo para enviar a clientes.
- `promos/CODIGO.jpg`: promoción cuadrada 1080x1080 por producto. Textos listos: `promos/textos-whatsapp.txt`.
- `reels/*.mp4`: 4 videos verticales 9:16 (cámaras, grabadores y redes, intercom, acceso y alarmas). Diapositivas sueltas en cada carpeta.
- `scgv-inventario.csv`: para importar al inventario del SCGV (precio vacío, existencia 0).
- `img/`: foto limpia de cada producto. `productos.json`: datos fuente.
- Regenerar: `python3 tools/extraer.py catalogo.pdf crops/` y `python3 tools/generar.py crops/`.
