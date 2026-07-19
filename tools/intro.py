#!/usr/bin/env python3
"""Build the opening for an episode's motion-comic: a HERO poster (name + real epithets/legends on
the hero art) and a historic INDIA MAP poster with the location highlighted, both voiced in simple
vivid words. Prepends `hero` + `map` scenes to <eid>.player.json (run voice.py first).

  cd tools; $env:PYTHONIOENCODING="utf-8"; python intro.py rani_lakshmibai_s_stand_at_kotah_ki_serai
"""
import argparse, json, sys
sys.stdout.reconfigure(encoding="utf-8")
import aiclient as ai
import style_bible as sb
import common as C
import voice

INTRO_SYS = """You are a historian and film-trailer writer. Given a REAL historic Indian figure and \
their episode, write a HERO INTRO for a title poster and a MAP card. Be HISTORICALLY ACCURATE. Use \
SIMPLE, vivid, emotional words that make a reader FEEL it (no big or archaic words).

Return STRICT JSON only:
{
 "epithets": ["<3-4 short REAL titles/epithets the figure is truly known by>"],
 "legend_line": "<one short, powerful line of their legend, <=12 words>",
 "hero_intro": "<1-2 simple vivid sentences introducing the hero and the stakes, <=38 words>",
 "map_label": "<the place, short, e.g. 'Jhansi & Gwalior, Bundelkhand'>",
 "map_narration": "<one simple vivid sentence placing us in this land, <=26 words>",
 "mapX": <number 0..1, west(0)->east(1) position of the place on a north-up map of India>,
 "mapY": <number 0..1, north(0)->south(1) position of the place on a north-up map of India>
}"""

MAP_PROMPT = (
    "An antique, aged-parchment ILLUSTRATED MAP of the Indian subcontinent (India), north up, the "
    "whole landmass filling the frame from the Himalayas at the top to the southern tip at the "
    "bottom, coastline, hills and major rivers hand-drawn in old cartography style, warm sepia, "
    "gold and faded-ink tones, a faint decorative compass rose in a corner, soft vignette. "
    "Absolutely NO text, NO labels, NO letters or numbers anywhere. Cinematic, painterly.")


def _voice_line(text, mp3, wj):
    if mp3.exists() and wj.exists():
        return C.load_json(wj, {}).get("words", [])
    v, rate = voice.voice_for("narrator", "en")
    w = voice.Synth().say(text, mp3, v, rate)
    C.save_json(wj, {"words": w})
    return w


def build_intro(eid, langs=("en",), tok=None):
    pj = C.APP / "data" / f"{eid}.player.json"
    man = C.load_json(pj, None)
    if not man:
        sys.exit(f"no player manifest for {eid} (run: python voice.py {eid} --langs en)")
    rec = C.load_json(C.APP / "data" / f"{eid}.json", {})
    ent = C.registry_get(C.slug(rec.get("figure", eid))) or {}
    tok = tok or ai.token()

    print("  hero dossier", flush=True)
    user = json.dumps({k: rec.get(k, "") for k in ("title", "figure", "era", "region", "moral")}
                      | {"logline": (C.find_episode(eid) or {}).get("logline", "")}, ensure_ascii=False)
    d, tok = ai.chat_json(INTRO_SYS, user, tok=tok, max_tokens=1200)

    idir = C.APP / "assets" / eid / "intro"
    idir.mkdir(parents=True, exist_ok=True)
    print("  india map", flush=True)
    mp = idir / "map.png"
    if not mp.exists():
        tok = ai.gen_image(f"{sb.HOUSE_LOOK}\n\n{MAP_PROMPT}", mp, tok, size="1024x1536")

    adir = C.APP / "assets" / eid / "audio" / "intro"
    print("  intro voice", flush=True)
    htext, hwords, tok = voice.voice_multi(d.get("hero_intro", ""), adir, "hero", langs, "narrator", tok)
    mtext, mwords, tok = voice.voice_multi(d.get("map_narration", ""), adir, "map", langs, "narrator", tok)
    hero_audio = {lg: f"assets/{eid}/audio/intro/hero_{lg}.mp3" for lg in langs}
    map_audio = {lg: f"assets/{eid}/audio/intro/map_{lg}.mp3" for lg in langs}

    cover_art = f"assets/{eid}/img/cover.png"
    hero = {"id": "intro_hero", "type": "hero", "mood": "triumph",
            "art": cover_art, "name": ent.get("display_name", rec.get("figure", "")),
            "epithets": d.get("epithets", []), "legend": d.get("legend_line", ""),
            "era": rec.get("era", ""),
            "lines": [{"type": "narration", "role": "narrator", "text": htext,
                       "audio": hero_audio, "words": hwords}]}
    mapsc = {"id": "intro_map", "type": "map", "mood": "suspense",
             "map": f"assets/{eid}/intro/map.png", "x": d.get("mapX", 0.45), "y": d.get("mapY", 0.35),
             "label": d.get("map_label", rec.get("region", "")),
             "lines": [{"type": "narration", "role": "narrator", "text": mtext,
                        "audio": map_audio, "words": mwords}]}

    man["panels"] = [p for p in man["panels"] if p.get("id") not in ("intro_hero", "intro_map")]
    man["panels"] = [hero, mapsc] + man["panels"]
    man["hero"] = {"name": hero["name"], "epithets": hero["epithets"], "legend": hero["legend"]}
    C.save_json(pj, man)
    print(f"  DONE intro: hero '{hero['name']}' + map '{mapsc['label']}' ({d.get('mapX')},{d.get('mapY')})",
          flush=True)
    return tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eid")
    ap.add_argument("--langs", nargs="*", default=["en"])
    a = ap.parse_args()
    ep = C.find_episode(a.eid)
    build_intro(ep["id"] if ep else a.eid, langs=a.langs)


if __name__ == "__main__":
    main()
