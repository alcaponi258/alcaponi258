# Escala x4 con IA (EDSR) las fotos pequeñas. Uso: escalar.py modelo.pb carpeta [lado_min]
import cv2, sys, os, glob, time
sr = cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(sys.argv[1]); sr.setModel('edsr', 4)
lim = int(sys.argv[3]) if len(sys.argv) > 3 else 700; t = time.time(); n = 0
for f in glob.glob(os.path.join(sys.argv[2], '*.png')):
    im = cv2.imread(f, cv2.IMREAD_UNCHANGED)
    if im is None or max(im.shape[:2]) >= lim: continue
    if im.ndim == 3 and im.shape[2] == 4:   # fondo blanco si trae transparencia
        a = im[:, :, 3:4] / 255.0; im = (im[:, :, :3] * a + 255 * (1 - a)).astype('uint8')
    cv2.imwrite(f, sr.upsample(im)); n += 1
print(n, 'escaladas en', round(time.time() - t), 's')
