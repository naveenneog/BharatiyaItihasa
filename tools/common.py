#!/usr/bin/env python3
"""Shared helpers for the Indian History anime-comic engine: paths, slugs, the character
registry, and loading episodes from indian_history_collection.json."""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
APP = ROOT / "app"
CHARS = ROOT / "characters"
COLLECTION = ROOT / "indian_history_collection.json"
REGISTRY = CHARS / "registry.json"

LANGS = ["en", "kn", "hi", "ta", "te", "de"]


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")
    return re.sub(r"_+", "_", s)[:48]


def load_json(p, default):
    p = pathlib.Path(p)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(p, obj):
    p = pathlib.Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------- character registry ----------------

def load_registry():
    return load_json(REGISTRY, {"characters": {}})


def registry_get(figkey):
    return load_registry()["characters"].get(figkey)


def registry_put(figkey, entry):
    reg = load_registry()
    reg["characters"][figkey] = entry
    save_json(REGISTRY, reg)
    return entry


# ---------------- collection -> episodes ----------------

def _facts_from(ep):
    bits = []
    for s in ep.get("sources", []) or []:
        c = s.get("citation", "")
        if c:
            bits.append(c)
    if ep.get("notes"):
        bits.append("NOTE: " + ep["notes"])
    return " | ".join(bits)


def episode_record(ep, series_title):
    """Normalise a collection episode into the engine's EP dict."""
    return {
        "id": slug(ep.get("title", "")),
        "title": ep.get("title", ""),
        "figure": ep.get("figure", ep.get("title", "")),
        "era": ep.get("era", ""),
        "region": ep.get("region", ""),
        "series": series_title,
        "age": ep.get("age", "C"),
        "logline": ep.get("logline", ""),
        "moral": ep.get("moral", ""),
        "sources": ep.get("sources", []),
        "notes": ep.get("notes", ""),
        "facts": _facts_from(ep),
    }


def load_episodes():
    coll = load_json(COLLECTION, {"series": []})
    out = []
    for s in coll.get("series", []):
        for b in s.get("books", []):
            for ep in b.get("episodes", []):
                out.append(episode_record(ep, s.get("title", "")))
    return out


def find_episode(query):
    """Find an episode by id, exact title, or figure substring."""
    q = query.lower()
    eps = load_episodes()
    for e in eps:
        if e["id"] == query or e["title"].lower() == q:
            return e
    for e in eps:
        if q in e["figure"].lower() or q in e["title"].lower():
            return e
    return None
