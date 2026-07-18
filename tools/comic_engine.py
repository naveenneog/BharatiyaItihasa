#!/usr/bin/env python3
"""The character-consistent anime-comic engine.

For one episode: ensure its figure has a model sheet (gen_character), author a shonen-manga
storyboard with dialogue (gpt-4o), render every panel with gpt-image-2 images/edits feeding the
figure's model sheet as reference (so the character stays identical), composite the dialogue /
caption / SFX lettering overlay, assemble a comic page, and write a data record.

  cd tools; $env:PYTHONIOENCODING="utf-8"
  python comic_engine.py "Rani Lakshmibai"          # by figure/title/id (from the collection)
  python comic_engine.py "Ashoka" --max 4           # cap panels (faster)
  python comic_engine.py --n 5                       # batch the next 5 unbuilt episodes
"""
import argparse, sys

sys.stdout.reconfigure(encoding="utf-8")
import aiclient as ai
import style_bible as sb
import lettering as lt
import common as C
import gen_character as gc


def author_storyboard(ep, roster, tok):
    story, tok = ai.chat_json(sb.STORYBOARD_SYS, sb.storyboard_user(ep, roster), tok=tok,
                              max_tokens=4500)
    return story, tok


def _panel_prompt(ep, panel, cast_entries):
    refdesc = " ".join(e["ref_desc"] for e in cast_entries)
    era = sb.era_modifier(ep.get("era", ""), ep.get("series", ""), ep.get("region", ""))
    keep = (f"RECURRING CHARACTER (keep identical to the reference sheet): {refdesc}\n"
            if cast_entries else "")
    return (f"{sb.PANEL_STYLE}\n\n{era}\n\n{keep}"
            f"SHOT: {panel.get('shot', '')}\nACTION: {panel.get('action', '')}")


def render_episode(ep, tok=None, max_panels=None, force=False, co_stars=None):
    tok = tok or ai.token()
    eid = ep["id"]
    print(f"\n=== {eid} :: {ep['title']} ({ep.get('era','')}) ===", flush=True)

    # 1. ensure the lead (and any explicitly-requested co-stars) have model sheets
    lead, tok = gc.ensure_character(ep["figure"], ep.get("era", ""), ep.get("region", ""),
                                    ep.get("facts", ""), tok=tok)
    roster = {C.slug(ep["figure"]): lead["display_name"]}
    for cs in (co_stars or []):
        ent, tok = gc.ensure_character(cs, ep.get("era", ""), ep.get("region", ""), tok=tok)
        roster[C.slug(cs)] = ent["display_name"]

    # 2. author the storyboard
    print("  author storyboard", flush=True)
    story, tok = author_storyboard(ep, roster, tok)
    panels = story.get("panels", [])
    if max_panels:
        panels = panels[:max_panels]
    C.save_json(C.APP / "data" / f"{eid}.storyboard.json", {**story, "panels": panels})

    # 3. render + letter each panel
    rawdir = C.APP / "assets" / eid / "img"
    letterdir = C.APP / "assets" / eid / "panels"
    rawdir.mkdir(parents=True, exist_ok=True)
    letterdir.mkdir(parents=True, exist_ok=True)
    reg = C.load_registry()["characters"]
    out_panels, lettered = [], []
    for p in panels:
        pid = p["id"]
        cast = [c for c in p.get("cast", []) if c in reg]
        entries = [reg[c] for c in cast]
        raw = rawdir / f"{pid}.png"
        if force or not raw.exists():
            print(f"  panel {pid} ({', '.join(cast) or 'scenery'})", flush=True)
            prompt = _panel_prompt(ep, p, entries)
            if entries:
                refs = [C.APP / e["sheet"] for e in entries]
                tok = ai.edit_image(prompt, refs, raw, tok, size="1024x1024")
            else:
                tok = ai.gen_image(prompt, raw, tok, size="1024x1024")
        if not raw.exists():
            print(f"    skip {pid} (blocked/failed)", flush=True)
            continue
        letimg = letterdir / f"{pid}.jpg"
        lt.letter_panel(raw, p, letimg)
        lettered.append(letimg)
        out_panels.append({"id": pid, "image": f"assets/{eid}/panels/{pid}.jpg",
                           "shot": p.get("shot", ""), "sfx": p.get("sfx", []),
                           "dialogue": p.get("dialogue", [])})

    if not lettered:
        print("  NO panels rendered — aborting page", flush=True)
        return None, tok

    # 4. compose the comic page
    (C.APP / "comics").mkdir(parents=True, exist_ok=True)
    page = C.APP / "comics" / f"{eid}.jpg"
    lt.compose_page(lettered, page, title=ep["title"].upper(), cols=2)

    # 5. data record
    cover = out_panels[0]["image"]
    C.save_json(C.APP / "data" / f"{eid}.json", {
        "id": eid, "series": ep.get("series", ""), "title": ep["title"],
        "subtitle": story.get("subtitle", ""), "figure": ep["figure"],
        "era": ep.get("era", ""), "region": ep.get("region", ""), "age": ep.get("age", ""),
        "moral": ep.get("moral", ""), "sources": ep.get("sources", []),
        "cover": cover, "page": f"comics/{eid}.jpg", "panels": out_panels,
    })
    print(f"  DONE {eid}: {len(out_panels)} panels -> {page.name}", flush=True)
    return page, tok


def batch(n, max_panels=None, force=False):
    tok = ai.token()
    done = 0
    for ep in C.load_episodes():
        if done >= n:
            break
        if (C.APP / "data" / f"{ep['id']}.json").exists() and not force:
            continue
        try:
            _, tok = render_episode(ep, tok=tok, max_panels=max_panels, force=force)
            done += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {ep['id']}: {e}", flush=True)
    print(f"\nBATCH DONE: {done} episode(s)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="figure name / title / episode id")
    ap.add_argument("--n", type=int, help="batch: render the next N unbuilt episodes")
    ap.add_argument("--max", type=int, dest="max_panels", help="cap panels per episode")
    ap.add_argument("--co-stars", nargs="*", default=[], help="extra figures to design + feature")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    if a.n:
        batch(a.n, max_panels=a.max_panels, force=a.force)
        return
    if not a.query:
        sys.exit("provide a figure/title/id, or --n <count>")
    ep = C.find_episode(a.query)
    if not ep:
        sys.exit(f"no episode matches {a.query!r}")
    render_episode(ep, max_panels=a.max_panels, force=a.force, co_stars=a.co_stars)


if __name__ == "__main__":
    main()
