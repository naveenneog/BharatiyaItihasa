#!/usr/bin/env python3
"""Assemble a self-contained dist/ for CDN deploy (Firebase Hosting), containing ONLY the
QA-approved, completed stories listed in deploy/approved.json.

  * app shell (index.html + player/) is copied as-is,
  * a gated data/episodes.json is generated (approved stories are playable; the rest show as
    "coming soon" so the chapter roadmap still reads),
  * each approved story's manifest + assets are copied, with PNG art re-encoded to WebP
    (smaller) and the manifest/thumb paths rewritten .png -> .webp; audio (mp3) is copied as-is.

The reader loads data/ + assets/ RELATIVE to its own origin, so dist/ works unchanged on any static
host. Run:  python tools/publish.py
"""
import json, os, pathlib, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
import common as C
import gallery
from PIL import Image

ROOT, APP = C.ROOT, C.APP
DIST = ROOT / "dist"
APPROVED_FILE = ROOT / "deploy" / "approved.json"
MAXW, Q = 1600, 80


def _webp(rel):
    return rel[:-4] + ".webp" if rel.lower().endswith(".png") else rel


def _rewrite(obj):
    if isinstance(obj, dict):
        return {k: _rewrite(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_rewrite(v) for v in obj]
    if isinstance(obj, str) and obj.lower().endswith(".png"):
        return obj[:-4] + ".webp"
    return obj


def _dump(obj, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def _to_webp(src, dst):
    im = Image.open(src)
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "WEBP", quality=Q, method=4)


def main():
    approved = list(dict.fromkeys(json.loads(APPROVED_FILE.read_text(encoding="utf-8"))["approved"]))
    approved = [e for e in approved if (APP / "data" / f"{e}.player.json").exists()]
    print(f"publishing {len(approved)} approved stories", flush=True)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # app shell
    shutil.copy(APP / "index.html", DIST / "index.html")
    shutil.copytree(APP / "player", DIST / "player")

    # gated + png->webp episodes.json (thumbs)
    gallery.build(approved=set(approved), out=DIST / "data" / "episodes.json")
    _dump(_rewrite(json.loads((DIST / "data" / "episodes.json").read_text(encoding="utf-8"))),
          DIST / "data" / "episodes.json")

    imgs = auds = 0
    for eid in approved:
        man = C.load_json(APP / "data" / f"{eid}.player.json", None)
        if not man:
            continue
        _dump(_rewrite(man), DIST / "data" / f"{eid}.player.json")
        adir = APP / "assets" / eid
        for root, _, files in os.walk(adir):
            for f in files:
                src = pathlib.Path(root) / f
                rel = src.relative_to(APP).as_posix()
                if f.lower().endswith(".png"):
                    _to_webp(src, DIST / _webp(rel)); imgs += 1
                elif f.lower().endswith(".mp3"):
                    dst = DIST / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(src, dst); auds += 1

    n = sum(1 for _ in DIST.rglob("*") if _.is_file())
    mb = round(sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file()) / 1048576, 1)
    print(f"dist/ assembled: {n} files, {mb} MB ({imgs} images -> webp, {auds} audio), "
          f"{len(approved)} stories", flush=True)


if __name__ == "__main__":
    main()
