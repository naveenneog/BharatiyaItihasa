#!/usr/bin/env python3
"""Chromium-based multilingual comic letterer.

Renders a full comic PAGE per language as HTML (title + panel grid + CSS speech/shout/thought
bubbles + caption bars + manga SFX) and screenshots it. Chromium shapes Indic scripts correctly
(HarfBuzz) using Nirmala UI, which PIL cannot do without libraqm. The panel ART is text-free, so
the same art is reused for every language; only this lettering layer changes.
"""
import html, math, pathlib, tempfile
from playwright.sync_api import sync_playwright

PANEL_PX = 700           # displayed size of each square panel
COLS = 2

FONT = {
    "en": '"Comic Sans MS","Segoe UI",sans-serif',
    "de": '"Comic Sans MS","Segoe UI",sans-serif',
    "hi": '"Nirmala UI","Noto Sans Devanagari",sans-serif',
    "kn": '"Nirmala UI","Noto Sans Kannada",sans-serif',
    "ta": '"Nirmala UI","Noto Sans Tamil",sans-serif',
    "te": '"Nirmala UI","Noto Sans Telugu",sans-serif',
}
TITLE_FONT = {"en": '"Impact","Arial Black",sans-serif', "de": '"Impact","Arial Black",sans-serif'}


def _star(points=11, inner=0.66):
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points - math.pi / 2
        r = 50 if i % 2 == 0 else 50 * inner
        pts.append(f"{50 + r * math.cos(ang):.1f}% {50 + r * math.sin(ang):.1f}%")
    return "polygon(" + ",".join(pts) + ")"


_STAR = _star()


def _txt(dl, lang):
    return (dl.get("i18n", {}).get(lang) if lang != "en" else None) or dl.get("text", "")


def _css(lang):
    fam = FONT.get(lang, FONT["en"])
    tfam = TITLE_FONT.get(lang, fam)
    return f"""
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:#0c0c0e; font-family:{fam}; }}
    #page {{ width:{COLS*PANEL_PX + (COLS+1)*16}px; padding:16px; background:#0c0c0e; }}
    #title {{ font-family:{tfam}; color:#f0e2cd; text-align:center; font-weight:900;
              font-size:46px; letter-spacing:1px; padding:6px 0 18px; }}
    #grid {{ display:flex; flex-wrap:wrap; gap:16px; justify-content:center; }}
    .panel {{ position:relative; width:{PANEL_PX}px; height:{PANEL_PX}px; overflow:hidden;
              border:3px solid #ebe8e2; background:#222; }}
    .panel img {{ width:100%; height:100%; object-fit:cover; display:block; }}
    .ov {{ position:absolute; inset:0; display:flex; flex-direction:column;
           align-items:flex-start; gap:12px; padding:16px; }}
    .bubble {{ background:#fff; color:#16161c; border:3px solid #16161c; border-radius:22px;
               padding:10px 15px; max-width:64%; font-weight:700; font-size:21px; line-height:1.15;
               position:relative; }}
    .bubble.r {{ align-self:flex-end; }}
    .bubble::after {{ content:""; position:absolute; bottom:-15px; left:26px; width:0; height:0;
               border:9px solid transparent; border-top-color:#fff; }}
    .bubble.r::after {{ left:auto; right:26px; }}
    .shout {{ background:#fff; color:#b30f22; border:none; text-transform:uppercase;
              font-weight:800; font-size:23px; padding:16px 22px; max-width:60%;
              clip-path:{_STAR}; text-align:center; }}
    .shout::after {{ display:none; }}
    .shout-wrap {{ position:relative; }}
    .shout-wrap::before {{ content:""; position:absolute; inset:-5px; background:#16161c;
              clip-path:{_STAR}; z-index:-1; }}
    .thought {{ background:#fff; color:#16161c; border:3px solid #16161c; border-radius:50%/38%;
              padding:14px 22px; max-width:60%; font-weight:700; font-size:20px; font-style:italic; }}
    .thought::after {{ display:none; }}
    .cap {{ background:rgba(16,14,18,.9); color:#f5f0e6; border-left:8px solid #b0202a;
            padding:8px 13px; font-weight:700; font-size:19px; max-width:88%; }}
    .cap.place {{ margin-top:auto; font-size:17px; }}
    .sfx {{ position:absolute; font-family:"Impact","Arial Black",sans-serif; color:#d62828;
            -webkit-text-stroke:3px #14141a; font-size:64px; font-weight:900; z-index:0;
            white-space:nowrap; }}
    """


def _panel_html(p, lang, art_uri):
    ov = []
    sfx = []
    # SFX (behind bubbles)
    for i, s in enumerate(p.get("sfx", []) or []):
        left = 62 if i % 2 == 0 else 8
        top = 60 if i % 2 == 0 else 44
        rot = -12 if i % 2 == 0 else 9
        sfx.append(f'<div class="sfx" style="left:{left}%;top:{top}%;transform:rotate({rot}deg)">'
                   f'{html.escape(s.upper())}</div>')
    # ordered overlay: narration (top) -> bubbles -> place caption (bottom)
    narr = [d for d in p.get("dialogue", []) if d.get("type") == "narration"]
    place = [d for d in p.get("dialogue", []) if d.get("type") == "caption"]
    bubbles = [d for d in p.get("dialogue", []) if d.get("type") in ("speech", "shout", "thought")]
    for d in narr:
        ov.append(f'<div class="cap">{html.escape(_txt(d, lang))}</div>')
    for i, d in enumerate(bubbles):
        t = d.get("type"); side = "r" if i % 2 else ""
        txt = html.escape(_txt(d, lang))
        if t == "shout":
            ov.append(f'<div class="shout-wrap {side}" style="align-self:{"flex-end" if side else "flex-start"}">'
                      f'<div class="shout">{txt}</div></div>')
        elif t == "thought":
            ov.append(f'<div class="thought {side}">{txt}</div>')
        else:
            ov.append(f'<div class="bubble {side}">{txt}</div>')
    for d in place:
        ov.append(f'<div class="cap place">{html.escape(_txt(d, lang))}</div>')
    return (f'<div class="panel"><img src="{art_uri}">' + "".join(sfx)
            + '<div class="ov">' + "".join(ov) + '</div></div>')


def _page_html(title, panels, lang, art_uris):
    cells = "".join(_panel_html(p, lang, art_uris[p["id"]]) for p in panels if p["id"] in art_uris)
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{_css(lang)}</style></head>'
            f'<body><div id="page"><div id="title">{html.escape(title)}</div>'
            f'<div id="grid">{cells}</div></div></body></html>')


def render_pages(eid, story, art_dir, out_dir, langs):
    """Render one comic page per language. Returns {lang: Path}. Art is read from art_dir/<pid>.png."""
    art_dir = pathlib.Path(art_dir)
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    panels = [p for p in story.get("panels", []) if (art_dir / f"{p['id']}.png").exists()]
    art_uris = {p["id"]: (art_dir / f"{p['id']}.png").resolve().as_uri() for p in panels}
    out = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": COLS * PANEL_PX + 80, "height": 1000},
                                device_scale_factor=2)
        for lang in langs:
            title = story.get("title_i18n", {}).get(lang) or story.get("title_i18n", {}).get("en", eid)
            doc = _page_html(title, panels, lang, art_uris)
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
                f.write(doc); tmp = f.name
            page.goto(pathlib.Path(tmp).as_uri())
            page.wait_for_timeout(250)
            el = page.query_selector("#page")
            dest = out_dir / f"{lang}.jpg"
            el.screenshot(path=str(dest), type="jpeg", quality=90)
            pathlib.Path(tmp).unlink(missing_ok=True)
            out[lang] = dest
            print(f"    page[{lang}] -> {dest}", flush=True)
        browser.close()
    return out
