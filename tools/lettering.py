#!/usr/bin/env python3
"""Comic lettering: composite dialogue bubbles, caption boxes and manga SFX onto a clean
panel image, and assemble panels into a comic page. Art is generated text-free; this overlays
a crisp vector-style lettering layer (so one panel can be re-lettered per language later).
"""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont

FONTS = "C:/Windows/Fonts"
_F = {}


def font(size, kind="speech"):
    files = {"speech": "comicbd.ttf", "thought": "comicbd.ttf", "shout": "impact.ttf",
             "sfx": "impact.ttf", "caption": "ariblk.ttf", "title": "impact.ttf"}
    key = (kind, size)
    if key not in _F:
        try:
            _F[key] = ImageFont.truetype(f"{FONTS}/{files.get(kind,'comicbd.ttf')}", size)
        except Exception:
            _F[key] = ImageFont.load_default()
    return _F[key]


def _wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def _text_box(draw, lines, fnt, line_gap=4):
    w = max((draw.textlength(l, font=fnt) for l in lines), default=0)
    asc, desc = fnt.getmetrics()
    lh = asc + desc + line_gap
    return int(w), int(lh * len(lines)), lh


def _draw_lines(draw, lines, fnt, x, y, lh, fill=(20, 20, 25), center_w=None):
    for i, l in enumerate(lines):
        lx = x
        if center_w is not None:
            lx = x + (center_w - draw.textlength(l, font=fnt)) / 2
        draw.text((lx, y + i * lh), l, font=fnt, fill=fill)


def _speech_bubble(base, cx, cy, lines, fnt, kind="speech", tail_to=None):
    """Draw a bubble centered near (cx,cy). Returns nothing; edits `base` in place."""
    d = ImageDraw.Draw(base)
    tw, th, lh = _text_box(d, lines, fnt)
    padx, pady = 26, 20
    bw, bh = tw + 2 * padx, th + 2 * pady
    x0, y0 = int(cx - bw / 2), int(cy - bh / 2)
    x1, y1 = x0 + bw, y0 + bh
    outline, ow = (20, 20, 25), 5

    # tail toward a target point (character), drawn before the bubble body
    if tail_to and kind in ("speech", "shout"):
        txp, typ = tail_to
        bx, by = (x0 + x1) / 2, (y1 if typ > cy else y0)
        d.polygon([(bx - 26, by), (bx + 26, by), (txp, typ)], fill=(255, 255, 255),
                  outline=outline)

    if kind == "shout":
        pts, n, rx, ry = [], 20, bw / 2 + 16, bh / 2 + 14
        for i in range(n * 2):
            ang = math.pi * i / n
            r = 1.0 if i % 2 == 0 else 0.74
            pts.append((cx + math.cos(ang) * rx * r, cy + math.sin(ang) * ry * r))
        d.polygon(pts, fill=(255, 255, 255), outline=outline)
        for i in range(1, ow):
            d.polygon(pts, outline=outline)
    elif kind == "thought":
        d.ellipse([x0, y0, x1, y1], fill=(255, 255, 255), outline=outline, width=ow)
        if tail_to:
            txp, typ = tail_to
            for k, rr in enumerate((13, 9, 6)):
                px = x0 + bw * 0.3 + (txp - (x0 + bw * 0.3)) * (k + 1) / 4
                py = y1 + (typ - y1) * (k + 1) / 4
                d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(255, 255, 255), outline=outline, width=3)
    else:  # speech
        d.rounded_rectangle([x0, y0, x1, y1], radius=int(bh * 0.42),
                            fill=(255, 255, 255), outline=outline, width=ow)

    _draw_lines(d, lines, fnt, x0 + padx, y0 + pady, lh, center_w=tw)


def _caption(base, text, fnt, where="top", accent=(176, 30, 42)):
    d = ImageDraw.Draw(base, "RGBA")
    W, H = base.size
    margin = 24
    max_w = W - 2 * margin - 40
    lines = _wrap(d, text, fnt, max_w)
    tw, th, lh = _text_box(d, lines, fnt)
    bw, bh = tw + 40, th + 28
    if where == "top":
        x0, y0 = margin, margin
    else:  # bottom-left small place/date caption
        x0, y0 = margin, H - bh - margin
    d.rectangle([x0, y0, x0 + bw, y0 + bh], fill=(18, 16, 20, 232))
    d.rectangle([x0, y0, x0 + 9, y0 + bh], fill=accent + (255,))
    _draw_lines(d, lines, fnt, x0 + 22, y0 + 14, lh, fill=(245, 240, 230))


def _sfx(base, text, cx, cy, size, rot=-12):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fnt = font(size, "sfx")
    tw = d.textlength(text, font=fnt)
    x, y = cx - tw / 2, cy - size / 2
    for ox in range(-6, 7, 2):
        for oy in range(-6, 7, 2):
            d.text((x + ox, y + oy), text, font=fnt, fill=(15, 12, 14, 255))
    d.text((x, y), text, font=fnt, fill=(214, 40, 40, 255))
    layer = layer.rotate(rot, resample=Image.BICUBIC, center=(int(cx), int(cy)))
    base.alpha_composite(layer)


# corner anchors (fraction of panel) used to place bubbles without covering the center subject
_ANCHORS = [(0.26, 0.17), (0.74, 0.17), (0.24, 0.30), (0.76, 0.30)]


def letter_panel(img_path, panel, out_path, bubble_font=34, caption_font=26):
    """Overlay a panel's dialogue + sfx. `panel` = storyboard panel dict."""
    base = Image.open(img_path).convert("RGBA")
    W, H = base.size
    d = ImageDraw.Draw(base)

    # SFX first (behind bubbles)
    for i, s in enumerate(panel.get("sfx", []) or []):
        cx = W * (0.68 if i % 2 == 0 else 0.30)
        cy = H * (0.62 if i % 2 == 0 else 0.44)
        _sfx(base, s.upper(), cx, cy, int(H * 0.13), rot=-12 if i % 2 == 0 else 9)

    bubble_i = 0
    for dl in panel.get("dialogue", []) or []:
        typ = dl.get("type", "speech")
        text = (dl.get("text") or "").strip()
        if not text:
            continue
        if typ in ("caption",):
            _caption(base, text, font(caption_font, "caption"), where="bottom")
            continue
        if typ in ("narration",):
            _caption(base, text, font(caption_font, "caption"), where="top")
            continue
        ax, ay = _ANCHORS[bubble_i % len(_ANCHORS)]
        cx, cy = W * ax, H * ay
        fkind = "shout" if typ == "shout" else ("thought" if typ == "thought" else "speech")
        fnt = font(bubble_font + (6 if typ == "shout" else 0), fkind)
        lines = _wrap(d, text if typ != "shout" else text.upper(), fnt, W * 0.30)
        tail = (W * ax, H * (ay + 0.16))
        _speech_bubble(base, cx, cy, lines, fnt, kind=fkind, tail_to=tail)
        bubble_i += 1

    base.convert("RGB").save(out_path, quality=92)
    return out_path


def compose_page(panel_paths, out_path, title=None, cols=2, bg=(12, 12, 14)):
    """Assemble lettered panels into a single comic page with manga gutters."""
    imgs = [Image.open(p).convert("RGB") for p in panel_paths]
    n = len(imgs)
    cols = 1 if n == 1 else cols
    rows = math.ceil(n / cols)
    cw = max(i.width for i in imgs)
    ch = max(i.height for i in imgs)
    gut = 16
    title_h = 96 if title else 0
    W = cols * cw + (cols + 1) * gut
    H = title_h + rows * ch + (rows + 1) * gut
    page = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(page)
    if title:
        tf = font(56, "title")
        tw = d.textlength(title, font=tf)
        d.text(((W - tw) / 2, (title_h - 56) / 2 + 6), title, font=tf, fill=(240, 226, 205))
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        x = gut + c * (cw + gut)
        y = title_h + gut + r * (ch + gut)
        im = im.resize((cw, ch)) if im.size != (cw, ch) else im
        page.paste(im, (x, y))
        d.rectangle([x - 2, y - 2, x + cw + 1, y + ch + 1], outline=(235, 232, 226), width=3)
    page.save(out_path, quality=92)
    return out_path
