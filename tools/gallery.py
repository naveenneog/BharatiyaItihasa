#!/usr/bin/env python3
"""Generate app/data/episodes.json for the home page.

Emits TWO views:
  * "chapters" — deeply-built collections (e.g. The Chola Empire), grouped by chapter_part and
    ordered, showing built stories (playable) and upcoming ones (coming soon).
  * "periods"  — era timelines (Ancient / Medieval / Freedom Struggle) for built episodes that are
    not (yet) part of a formal chapter.

  cd tools; python gallery.py
"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import common as C

FLAGSHIP = {"rani_lakshmibai_s_stand_at_kotah_ki_serai", "rajendra_brings_the_ganges_south",
            "shivaji_s_quiet_escape_from_agra", "ashoka_s_kalinga_change_of_heart"}
PERIODS = [
    {"key": "Ancient", "label": "Ancient India", "blurb": "Empires, dharma and the classical age", "hint": "up to ~700 CE"},
    {"key": "Medieval", "label": "Medieval India", "blurb": "Kingdoms, faith, sea-power and swaraj", "hint": "~700 - 1750 CE"},
    {"key": "Freedom Struggle", "label": "The Freedom Struggle", "blurb": "Revolt, resistance and a free India", "hint": "1750 - 1947"},
]
CHAPTER_BLURB = {"The Chola Empire": "A Tamil empire of temples, bronze, trade and the sea \u2014 its rise, its emperors, its genius and its long sunset."}


def parse_year(era):
    if not era:
        return None
    m = re.search(r'(\d+)\s*(?:st|nd|rd|th)?\s*century\s*(?:BCE|BC)\b', era, re.I)
    if m:
        return -((int(m.group(1)) - 1) * 100 + 50)
    m = re.search(r'(\d+)\s*(?:BCE|BC)\b', era, re.I)
    if m:
        return -int(m.group(1))
    m = re.search(r'(\d+)\s*(?:st|nd|rd|th)\s*century\b', era, re.I)
    if m:
        return (int(m.group(1)) - 1) * 100 + 50
    m = re.search(r'\b(\d{3,4})\b', era)
    return int(m.group(1)) if m else None


def year_label(y):
    return "" if y is None else (f"{-y} BCE" if y < 0 else f"{y} CE")


def period_of(series, year):
    if series and "Freedom" in series:
        return "Freedom Struggle"
    if year is None:
        return "Medieval"
    if year >= 1750:
        return "Freedom Struggle"
    return "Ancient" if year < 700 else "Medieval"


def item_for(ep, approved=None):
    eid = ep["id"]
    pj = C.APP / "data" / f"{eid}.player.json"
    built = pj.exists() and (approved is None or eid in approved)
    y = parse_year(ep.get("era", ""))
    it = {"id": eid, "figure": ep.get("figure", ""), "title": ep.get("title", ""),
          "era": ep.get("era", ""), "series": ep.get("series", ""), "built": built,
          "flagship": eid in FLAGSHIP, "chapter": ep.get("chapter", ""),
          "chapter_part": ep.get("chapter_part", ""), "chapter_order": ep.get("chapter_order", 999),
          "year": y if y is not None else 9999, "year_label": year_label(y),
          "legend": ep.get("logline", ""), "epithets": [], "scenes": 0, "langs": [], "thumb": ""}
    if built:
        d = C.load_json(pj, {})
        pans = d.get("panels", [])
        hero = next((p for p in pans if p.get("id") == "intro_hero"), None)
        cover = next((p for p in pans if p.get("id") == "cover"), None)
        h = d.get("hero", {})
        it.update({"thumb": (hero or {}).get("art") or (cover or {}).get("art") or (pans[0].get("art") if pans else ""),
                   "legend": h.get("legend", "") or ep.get("logline", ""),
                   "epithets": h.get("epithets", [])[:2], "scenes": len(pans),
                   "langs": d.get("langs", ["en"])})
    return it


def build(approved=None, out=None):
    eps = [item_for(e, approved) for e in C.load_episodes()]
    seen, uniq = set(), []
    for it in eps:
        if it["id"] not in seen:
            seen.add(it["id"]); uniq.append(it)
    eps = uniq

    # chapters (built + upcoming), grouped by part
    chap = {}
    for it in eps:
        if it["chapter"]:
            chap.setdefault(it["chapter"], {}).setdefault(it["chapter_part"], []).append(it)
    chapters = []
    for cname, parts in chap.items():
        pl = [{"part": pn, "episodes": sorted(parts[pn], key=lambda x: x["chapter_order"])}
              for pn in sorted(parts)]
        built_n = sum(1 for p in parts.values() for e in p if e["built"])
        total_n = sum(len(p) for p in parts.values())
        chapters.append({"chapter": cname, "blurb": CHAPTER_BLURB.get(cname, ""),
                         "built": built_n, "total": total_n, "parts": pl})
    chapters.sort(key=lambda c: -c["built"])

    # era timelines for built, non-chapter episodes
    by_period = {p["key"]: [] for p in PERIODS}
    for it in eps:
        if it["chapter"] or not it["built"]:
            continue
        by_period[period_of(it["series"], parse_year(it["era"]))].append(it)
    periods = []
    for p in PERIODS:
        e = sorted(by_period[p["key"]], key=lambda x: x["year"])
        rng = ""
        if e:
            lo, hi = e[0]["year_label"], e[-1]["year_label"]
            rng = lo if lo == hi else f"{lo} - {hi}"
        periods.append({**p, "range": rng, "count": len(e), "episodes": e})

    built_total = sum(1 for it in eps if it["built"])
    out = out or (C.APP / "data" / "episodes.json")
    C.save_json(out, {"built": built_total, "chapters": chapters, "periods": periods})
    cs = ", ".join(f"{c['chapter']} {c['built']}/{c['total']}" for c in chapters)
    print(f"episodes.json -> {out}: {built_total} built | chapters: {cs} | "
          f"timelines: {', '.join(f'{p['label']}:{p['count']}' for p in periods)}", flush=True)


if __name__ == "__main__":
    build()
