#!/usr/bin/env python3
"""Character registry + model-sheet generator.

For a historical figure: gpt-4o designs an era-accurate anime character bible, gpt-image-2
renders a full-body model sheet, and both are stored so the SAME design is reused across every
panel and every episode the figure appears in (cross-episode consistency).

  cd tools; $env:PYTHONIOENCODING="utf-8"
  python gen_character.py "Chhatrapati Shivaji Maharaj" --era "17th century Maratha" --region "Deccan"
  python gen_character.py --figure "Ashoka"        # pull era/region/facts from the collection
"""
import argparse, json, sys

sys.stdout.reconfigure(encoding="utf-8")
import aiclient as ai
import style_bible as sb
import common as C


def design_bible(figure, era="", region="", facts="", tok=None):
    bible, tok = ai.chat_json(sb.CHARACTER_SYS,
                              sb.character_user(figure, era, region, facts), tok=tok)
    return bible, tok


def render_sheet(bible, figkey, tok):
    sheetdir = C.APP / "assets" / "_characters" / figkey
    sheetdir.mkdir(parents=True, exist_ok=True)
    sheet = sheetdir / "sheet.png"
    prompt = f"{sb.SHEET_STYLE}\n\nCHARACTER: {bible.get('sheet_prompt', '')}"
    tok = ai.gen_image(prompt, sheet, tok, size="1024x1024")
    return sheet, tok


def ensure_character(figure, era="", region="", facts="", tok=None, force=False):
    """Return (registry_entry, tok). Generates the bible + sheet if missing (resumable)."""
    tok = tok or ai.token()
    figkey = C.slug(figure)
    existing = C.registry_get(figkey)
    sheet_abs = C.APP / (existing["sheet"] if existing else f"assets/_characters/{figkey}/sheet.png")
    if existing and sheet_abs.exists() and not force:
        return existing, tok

    print(f"  design character: {figure}", flush=True)
    bible, tok = design_bible(figure, era, region, facts, tok)
    bible["slug"] = figkey
    C.save_json(C.CHARS / f"{figkey}.json", bible)
    print(f"    ref_desc: {bible.get('ref_desc', '')[:110]}", flush=True)

    sheet, tok = render_sheet(bible, figkey, tok)
    if not sheet.exists():
        raise RuntimeError(f"model sheet failed for {figure}")

    entry = {"display_name": bible.get("display_name", figure),
             "figure": figure, "ref_desc": bible.get("ref_desc", ""),
             "sheet": f"assets/_characters/{figkey}/sheet.png"}
    C.registry_put(figkey, entry)
    print(f"  registered: {figkey}", flush=True)
    return entry, tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("figure", nargs="?", help="figure name")
    ap.add_argument("--figure", dest="figure_kw", help="lookup era/region/facts from the collection")
    ap.add_argument("--era", default="")
    ap.add_argument("--region", default="")
    ap.add_argument("--facts", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    figure, era, region, facts = a.figure, a.era, a.region, a.facts
    if a.figure_kw:
        ep = C.find_episode(a.figure_kw)
        if not ep:
            sys.exit(f"no episode matches {a.figure_kw!r}")
        figure = ep["figure"]; era = era or ep["era"]; region = region or ep["region"]
        facts = facts or ep["facts"]
    if not figure:
        sys.exit("provide a figure name or --figure <query>")

    entry, _ = ensure_character(figure, era, region, facts, force=a.force)
    print(json.dumps(entry, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
