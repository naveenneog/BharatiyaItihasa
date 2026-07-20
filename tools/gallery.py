#!/usr/bin/env python3
"""Generate app/data/episodes.json — the manifest the gallery home page (app/index.html) reads to
list every built motion-comic. Re-run any time new episodes finish.

  cd tools; python gallery.py
"""
import glob, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
import common as C

# flagships (bespoke, richest) surface first; the rest follow in build order
FLAGSHIP_ORDER = ["rani_lakshmibai_s_stand_at_kotah_ki_serai", "rajendra_brings_the_ganges_south",
                  "shivaji_s_quiet_escape_from_agra", "ashoka_s_kalinga_change_of_heart"]


def build():
    items = []
    for f in glob.glob(str(C.APP / "data" / "*.player.json")):
        d = C.load_json(f, {})
        eid = os.path.basename(f)[:-len(".player.json")]
        pans = d.get("panels", [])
        hero = next((p for p in pans if p.get("id") == "intro_hero"), None)
        cover = next((p for p in pans if p.get("id") == "cover"), None)
        thumb = (hero or {}).get("art") or (cover or {}).get("art") or (pans[0].get("art") if pans else "")
        h = d.get("hero", {})
        items.append({
            "id": eid,
            "figure": d.get("figure", ""),
            "title": d.get("title", eid),
            "title_i18n": d.get("title_i18n", {}),
            "era": d.get("era", ""),
            "epithets": h.get("epithets", [])[:2],
            "legend": h.get("legend", ""),
            "scenes": len(pans),
            "langs": d.get("langs", ["en"]),
            "thumb": thumb,
            "mtime": os.path.getmtime(f),
        })

    def rank(it):
        return (FLAGSHIP_ORDER.index(it["id"]) if it["id"] in FLAGSHIP_ORDER else 99, -it["mtime"])
    items.sort(key=rank)
    for it in items:
        it.pop("mtime", None)
    out = C.APP / "data" / "episodes.json"
    C.save_json(out, {"count": len(items), "episodes": items})
    print(f"wrote {out} ({len(items)} episodes)", flush=True)


if __name__ == "__main__":
    build()
