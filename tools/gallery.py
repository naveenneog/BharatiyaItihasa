#!/usr/bin/env python3
"""Generate app/data/episodes.json — the manifest the timeline home page (app/index.html) reads.

Groups every built motion-comic onto one of three era timelines (Ancient / Medieval / Freedom
Struggle) by parsing a year from its `era`, and sorts each timeline chronologically.

  cd tools; python gallery.py
"""
import glob, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import common as C

FLAGSHIP = {"rani_lakshmibai_s_stand_at_kotah_ki_serai", "rajendra_brings_the_ganges_south",
            "shivaji_s_quiet_escape_from_agra", "ashoka_s_kalinga_change_of_heart"}

PERIODS = [
    {"key": "Ancient", "label": "Ancient India", "blurb": "Empires, dharma and the classical age",
     "hint": "up to ~700 CE"},
    {"key": "Medieval", "label": "Medieval India", "blurb": "Kingdoms, faith, sea-power and swaraj",
     "hint": "~700 - 1750 CE"},
    {"key": "Freedom Struggle", "label": "The Freedom Struggle",
     "blurb": "Revolt, resistance and the fight for a free India", "hint": "1750 - 1947"},
]


def parse_year(era):
    """Return a sortable year (negative = BCE) parsed from an era string, or None."""
    if not era:
        return None
    m = re.search(r'(\d+)\s*(?:st|nd|rd|th)?\s*century\s*(?:BCE|BC)\b', era, re.I)
    if m:
        return -((int(m.group(1)) - 1) * 100 + 50)      # "3rd century BCE" -> -250
    m = re.search(r'(\d+)\s*(?:BCE|BC)\b', era, re.I)
    if m:
        return -int(m.group(1))                          # "326 BCE" -> -326
    m = re.search(r'(\d+)\s*(?:st|nd|rd|th)\s*century\b', era, re.I)
    if m:
        return (int(m.group(1)) - 1) * 100 + 50          # "16th century" -> 1550
    m = re.search(r'\b(\d{3,4})\b', era)
    if m:
        return int(m.group(1))                            # "1857", "1012-1044 CE" -> 1012
    return None


def year_label(y):
    if y is None:
        return ""
    return f"{-y} BCE" if y < 0 else f"{y} CE"


def period_of(series, year):
    if series and "Freedom" in series:
        return "Freedom Struggle"
    if year is None:
        return "Medieval"
    if year >= 1750:
        return "Freedom Struggle"
    if year < 700:
        return "Ancient"
    return "Medieval"


def build():
    by_period = {p["key"]: [] for p in PERIODS}
    for f in glob.glob(str(C.APP / "data" / "*.player.json")):
        d = C.load_json(f, {})
        eid = os.path.basename(f)[:-len(".player.json")]
        pans = d.get("panels", [])
        hero = next((p for p in pans if p.get("id") == "intro_hero"), None)
        cover = next((p for p in pans if p.get("id") == "cover"), None)
        thumb = (hero or {}).get("art") or (cover or {}).get("art") or (pans[0].get("art") if pans else "")
        rec = C.load_json(C.APP / "data" / f"{eid}.json", {})
        era = d.get("era", "") or rec.get("era", "")
        year = parse_year(era)
        h = d.get("hero", {})
        item = {
            "id": eid, "figure": d.get("figure", ""), "title": d.get("title", eid),
            "era": era, "year": year if year is not None else 9999, "year_label": year_label(year),
            "epithets": h.get("epithets", [])[:2], "legend": h.get("legend", ""),
            "scenes": len(pans), "langs": d.get("langs", ["en"]), "thumb": thumb,
            "flagship": eid in FLAGSHIP,
        }
        by_period[period_of(rec.get("series", ""), year)].append(item)

    periods, total = [], 0
    for p in PERIODS:
        eps = sorted(by_period[p["key"]], key=lambda x: x["year"])
        total += len(eps)
        rng = ""
        if eps:
            lo, hi = eps[0]["year_label"], eps[-1]["year_label"]
            rng = lo if lo == hi else f"{lo} - {hi}"
        periods.append({**p, "range": rng, "count": len(eps), "episodes": eps})
    C.save_json(C.APP / "data" / "episodes.json", {"count": total, "periods": periods})
    labels = ", ".join(f"{p['label']}:{p['count']}" for p in periods)
    print(f"wrote episodes.json - {total} episodes across {labels}", flush=True)


if __name__ == "__main__":
    build()
