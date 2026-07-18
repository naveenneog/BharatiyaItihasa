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
import common as C
import gen_character as gc


def author_storyboard(ep, roster, tok):
    story, tok = ai.chat_json(sb.STORYBOARD_SYS, sb.storyboard_user(ep, roster), tok=tok,
                              max_tokens=9000)
    return story, tok


def _panel_prompt(ep, panel, cast_entries):
    refdesc = " ".join(e["ref_desc"] for e in cast_entries)
    era = sb.era_modifier(ep.get("era", ""), ep.get("series", ""), ep.get("region", ""))
    keep = (f"RECURRING CHARACTER (keep identical to the reference sheet): {refdesc}\n"
            if cast_entries else "")
    return (f"{sb.PANEL_STYLE}\n\n{era}\n\n{keep}"
            f"SHOT: {panel.get('shot', '')}\nACTION: {panel.get('action', '')}")


def render_episode(ep, tok=None, max_panels=None, force=False, co_stars=None, langs=None):
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

    # 3. render each panel (text-free art) via images/edits with the model sheet reference
    rawdir = C.APP / "assets" / eid / "img"
    rawdir.mkdir(parents=True, exist_ok=True)
    reg = C.load_registry()["characters"]
    out_panels, rendered = [], 0
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
        rendered += 1
        out_panels.append({"id": pid, "shot": p.get("shot", ""), "sfx": p.get("sfx", []),
                           "dialogue": p.get("dialogue", [])})

    if not rendered:
        print("  NO panels rendered — aborting page", flush=True)
        return None, tok

    # 4. translate + render one comic PAGE per language (Chromium letterer)
    langs = langs or C.LANGS
    pages, tok = _finish_pages(eid, story, ep["title"], story.get("subtitle", ""), langs, tok)

    # 5. data record
    C.save_json(C.APP / "data" / f"{eid}.json", {
        "id": eid, "series": ep.get("series", ""), "title": ep["title"],
        "title_i18n": story.get("title_i18n", {}), "subtitle": story.get("subtitle", ""),
        "figure": ep["figure"], "era": ep.get("era", ""), "region": ep.get("region", ""),
        "age": ep.get("age", ""), "moral": ep.get("moral", ""), "sources": ep.get("sources", []),
        "langs": langs, "pages": {lg: f"comics/{eid}/{lg}.jpg" for lg in pages},
        "cover": f"assets/{eid}/img/{out_panels[0]['id']}.png", "panels": out_panels,
    })
    print(f"  DONE {eid}: {rendered} panels x {len(pages)} languages", flush=True)
    return pages.get("en"), tok


def _finish_pages(eid, story, title, subtitle, langs, tok):
    """Translate the storyboard (skips already-translated langs) and render a comic page per
    language from the text-free art. Shared by render + reletter."""
    import translate
    import weblettering
    tok = translate.translate_storyboard(story, title, subtitle, langs, tok=tok)
    C.save_json(C.APP / "data" / f"{eid}.storyboard.json", story)
    pages = weblettering.render_pages(eid, story, C.APP / "assets" / eid / "img",
                                      C.APP / "comics" / eid, langs)
    return pages, tok


def reletter_episode(eid, langs=None, tok=None):
    """Re-render the comic PAGES for an already-drawn episode from its saved storyboard + art:
    translate (cached) + Chromium letter per language. No image generation."""
    story = C.load_json(C.APP / "data" / f"{eid}.storyboard.json", None)
    rec = C.load_json(C.APP / "data" / f"{eid}.json", {})
    if not story:
        print(f"  no storyboard for {eid}"); return None
    langs = langs or rec.get("langs") or C.LANGS
    title = rec.get("title") or eid.replace("_", " ").title()
    pages, _ = _finish_pages(eid, story, title, story.get("subtitle", ""), langs, tok)
    if rec:
        rec["langs"] = langs
        rec["pages"] = {lg: f"comics/{eid}/{lg}.jpg" for lg in pages}
        C.save_json(C.APP / "data" / f"{eid}.json", rec)
    print(f"  RELETTERED {eid}: {len(pages)} language page(s)", flush=True)
    return pages


def rescript_episode(eid, tok=None, langs=None):
    """Rewrite an existing episode's words in the epic (Baahubali) voice WITHOUT regenerating art,
    then re-translate + re-letter. Uses the saved storyboard's panel actions as the visual anchor."""
    story = C.load_json(C.APP / "data" / f"{eid}.storyboard.json", None)
    rec = C.load_json(C.APP / "data" / f"{eid}.json", {})
    if not story:
        print(f"  no storyboard for {eid}"); return None, tok
    tok = tok or ai.token()
    ep = C.find_episode(eid) or {"title": rec.get("title", eid), "figure": rec.get("figure", ""),
                                 "era": rec.get("era", ""), "region": rec.get("region", ""),
                                 "age": rec.get("age", "C"), "logline": "", "moral": rec.get("moral", "")}
    meta = {k: ep.get(k, "") for k in ("title", "figure", "era", "region", "age", "logline", "moral")}
    panels_meta = [{"id": p["id"], "shot": p.get("shot", ""), "action": p.get("action", "")}
                   for p in story.get("panels", [])]
    print(f"  rescript {eid} in epic voice", flush=True)
    out, tok = ai.chat_json(sb.RESCRIPT_SYS, sb.rescript_user(meta, panels_meta), tok=tok, max_tokens=9000)
    new_by_id = {p.get("id"): p.get("dialogue", []) for p in out.get("panels", [])}
    for p in story.get("panels", []):
        if p["id"] in new_by_id:
            p["dialogue"] = new_by_id[p["id"]]
        p.pop("sfx", None)
    story["subtitle"] = out.get("subtitle", story.get("subtitle", ""))
    story.pop("title_i18n", None); story.pop("subtitle_i18n", None)   # force re-translation
    C.save_json(C.APP / "data" / f"{eid}.storyboard.json", story)
    langs = langs or rec.get("langs") or C.LANGS
    pages, tok = _finish_pages(eid, story, rec.get("title") or eid, story.get("subtitle", ""), langs, tok)
    if rec:
        rec["langs"] = langs
        rec["pages"] = {lg: f"comics/{eid}/{lg}.jpg" for lg in pages}
        C.save_json(C.APP / "data" / f"{eid}.json", rec)
    print(f"  RESCRIPTED {eid}: epic voice, {len(pages)} language page(s)", flush=True)
    return pages, tok


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
    ap.add_argument("--reletter", metavar="ID", help="re-letter an episode from its saved storyboard")
    ap.add_argument("--reletter-all", action="store_true", help="re-letter every built episode")
    ap.add_argument("--rescript", metavar="ID", help="rewrite an episode's words in the epic voice")
    ap.add_argument("--rescript-all", action="store_true", help="epic-rescript every built episode")
    ap.add_argument("--langs", nargs="*", help="languages (default: en kn hi ta te de)")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    langs = a.langs or C.LANGS

    if a.rescript_all:
        tok = None
        for f in sorted((C.APP / "data").glob("*.storyboard.json")):
            _, tok = rescript_episode(f.name[:-len(".storyboard.json")], tok=tok, langs=langs)
        return
    if a.rescript:
        rescript_episode(a.rescript, langs=langs)
        return
    if a.reletter_all:
        for f in sorted((C.APP / "data").glob("*.storyboard.json")):
            reletter_episode(f.name[:-len(".storyboard.json")], langs=langs)
        return
    if a.reletter:
        reletter_episode(a.reletter, langs=langs)
        return
    if a.n:
        batch(a.n, max_panels=a.max_panels, force=a.force)
        return
    if not a.query:
        sys.exit("provide a figure/title/id, or --n <count>")
    ep = C.find_episode(a.query)
    if not ep:
        sys.exit(f"no episode matches {a.query!r}")
    render_episode(ep, max_panels=a.max_panels, force=a.force, co_stars=a.co_stars, langs=langs)


if __name__ == "__main__":
    main()
