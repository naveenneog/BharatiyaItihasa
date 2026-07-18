#!/usr/bin/env python3
"""Background matting: turn a character rendered on a uniform background into a transparent
cut-out (gpt-image-2 has no native transparency). Flood-fills the background from the borders
(so same-coloured pixels INSIDE the character are kept), feathers the edge, and auto-crops.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage


def cutout(in_path, out_path, thresh=42, feather=1.4, margin=10):
    im = Image.open(in_path).convert("RGB")
    w, h = im.size
    work = im.copy()
    SEED = (0, 254, 1)  # sentinel colour the source is extremely unlikely to contain
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for c in seeds:
        try:
            ImageDraw.floodfill(work, c, SEED, thresh=thresh)
        except Exception:  # noqa: BLE001
            pass
    arr = np.asarray(work)
    bg = (arr[:, :, 0] == SEED[0]) & (arr[:, :, 1] == SEED[1]) & (arr[:, :, 2] == SEED[2])

    # foreground = not-background; fill interior holes, then keep the largest connected blob
    # (drops stray background wisps that the flood-fill couldn't reach).
    fg = ndimage.binary_fill_holes(~bg)
    lbl, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lbl), lbl, index=range(1, n + 1))
        fg = lbl == (int(np.argmax(sizes)) + 1)

    alpha = np.where(fg, 255, 0).astype(np.uint8)
    a = Image.fromarray(alpha, "L")
    if feather:
        a = a.filter(ImageFilter.GaussianBlur(feather))
    out = im.convert("RGBA")
    out.putalpha(a)
    bbox = out.getbbox()
    if bbox:
        bbox = (max(0, bbox[0] - margin), max(0, bbox[1] - margin),
                min(w, bbox[2] + margin), min(h, bbox[3] + margin))
        out = out.crop(bbox)
    out.save(out_path)
    return out.size


if __name__ == "__main__":
    import sys
    print(cutout(sys.argv[1], sys.argv[2]))
