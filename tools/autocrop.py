"""Conservative auto-crop: trim only edge rows/columns that are mostly wood table."""
import sys, os, glob, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

def wood_mask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / (mx + 1e-6)
    # wood is a fairly dark, saturated brown; aged paper and tape are lighter
    return (r > g) & (g > b) & (sat > 0.28) & (mx < 0.62) | (mx < 0.22)

def crop_box(im, thresh=0.6, pad=0.012):
    W, H = im.size
    s = 400 / max(W, H)
    a = np.asarray(im.resize((max(1, int(W * s)), max(1, int(H * s)))), dtype=np.float32) / 255
    m = ndi.binary_opening(wood_mask(a), iterations=1)
    h, w = m.shape
    rows, cols = m.mean(1), m.mean(0)
    def edge(v, rev=False):
        idx = range(len(v) - 1, -1, -1) if rev else range(len(v))
        for k, i in enumerate(idx):
            if v[i] < thresh:
                return k
        return 0
    t, b_, l, r = edge(rows), edge(rows, True), edge(cols), edge(cols, True)
    # second pass: recompute on the inner region so angled cards trim a bit more
    inner = m[t:h - b_, l:w - r]
    if inner.size:
        rows2, cols2 = inner.mean(1), inner.mean(0)
        t += edge(rows2); b_ += edge(rows2, True); l += edge(cols2); r += edge(cols2, True)
    x0 = max(0, l / w - pad); x1 = min(1, (w - r) / w + pad)
    y0 = max(0, t / h - pad); y1 = min(1, (h - b_) / h + pad)
    return (int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H))

if __name__ == '__main__':
    SRC, OUT = sys.argv[1], sys.argv[2]
    os.makedirs(OUT, exist_ok=True)
    report = {}
    for f in sorted(glob.glob(os.path.join(SRC, '*.jpg'))):
        name = os.path.basename(f)
        if name == 'box.jpg':
            continue
        im = Image.open(f).convert('RGB')
        box = crop_box(im)
        W, H = im.size
        trimmed = 1 - (box[2] - box[0]) * (box[3] - box[1]) / (W * H)
        if trimmed < 0.05:
            continue
        im.crop(box).save(os.path.join(OUT, name), quality=85, optimize=True)
        report[name] = round(trimmed, 2)
    json.dump(report, open(os.path.join(OUT, '_report.json'), 'w'), indent=1)
    print(len(report), 'cropped')
