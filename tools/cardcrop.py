"""Crop to the card: find the bright paper region containing the photo's center and take its bounding box."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

def card_box(im, pad=0.02):
    W, H = im.size
    s = 500 / max(W, H)
    a = np.asarray(im.resize((int(W * s), int(H * s))), dtype=np.float32) / 255
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / (mx + 1e-6)
    paper = ((mx > 0.55) & (sat < 0.38)) | (mx > 0.78)
    paper = ndi.binary_opening(paper, iterations=3)
    paper = ndi.binary_fill_holes(ndi.binary_closing(paper, iterations=6))
    lab, n = ndi.label(paper)
    h, w = paper.shape
    if n == 0:
        return None
    # component nearest the center
    c = lab[h // 2, w // 2]
    if c == 0:
        sizes = ndi.sum(paper, lab, range(1, n + 1)); c = int(np.argmax(sizes)) + 1
    ys, xs = np.where(lab == c)
    frac = len(ys) / (h * w)
    if frac < 0.08 or frac > 0.92:
        return None
    x0, x1, y0, y1 = xs.min() / w - pad, xs.max() / w + pad, ys.min() / h - pad, ys.max() / h + pad
    return (int(max(0, x0) * W), int(max(0, y0) * H), int(min(1, x1) * W), int(min(1, y1) * H))
