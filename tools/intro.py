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


CAST_INTRO_SYS = """You are a historian and film-trailer writer. Given a REAL historic figure and \
the episode they appear in, write a short CHARACTER INTRODUCTION card. Be HISTORICALLY ACCURATE. \
Use SIMPLE, vivid, emotional words that make a reader FEEL it (no big or archaic words).

Return STRICT JSON only:
{
 "epithets": ["<2-3 short REAL titles/epithets this person is truly known by>"],
 "legend_line": "<one short powerful line of who they are, <=11 words>",
 "intro": "<1-2 simple vivid sentences: who they are and their role in THIS story, <=34 words>"
}"""

CAST_PORTRAIT = (
    "{look}\n\nDRAMATIC WIDE CINEMATIC HERO-INTRODUCTION PORTRAIT of {name} ({ref}): {act}. The face "
    "and upper body are LARGE and centred in the MIDDLE of the frame with clear headroom above the "
    "head for a title; heroic low angle, cinematic rim-light, a richly illustrated atmospheric "
    "background that fits the era. Absolutely NO text, NO labels, NO letters or numbers anywhere.")


def add_cast_intro(eid, after_pid, figure, action_desc, era="", region="", facts="",
                   langs=("en",), mood="triumph", key=None, tok=None, reuse=True):
    """Introduce a supporting character with a hero-style card: a cinematic portrait (from their
    model sheet, so the face stays consistent) + real epithets/legend + a voiced one-line intro,
    inserted after `after_pid`. Gives co-stars their own moment instead of the hero in every scene."""
    import gen_character as gc
    pj = C.APP / "data" / f"{eid}.player.json"
    man = C.load_json(pj, None)
    if not man:
        sys.exit(f"no player manifest for {eid} (run: python voice.py {eid} --langs en)")
    tok = tok or ai.token()
    ent, tok = gc.ensure_character(figure, era, region, facts, tok=tok)
    key = key or C.slug(figure)
    d = C.APP / "assets" / eid / "cast"
    d.mkdir(parents=True, exist_ok=True)
    art = d / f"{key}.png"
    if not (reuse and art.exists()):
        print(f"  cast intro portrait: {ent['display_name']}", flush=True)
        tok = ai.edit_image(CAST_PORTRAIT.format(look=sb.HOUSE_LOOK, name=ent["display_name"],
                                                 ref=ent["ref_desc"], act=action_desc),
                            [C.APP / ent["sheet"]], art, tok, size="1536x1024")

    print(f"  cast dossier: {ent['display_name']}", flush=True)
    user = json.dumps({"figure": ent["display_name"], "role_in_scene": action_desc, "era": era,
                       "region": region, "facts": facts,
                       "episode": (C.find_episode(eid) or {}).get("logline", "")}, ensure_ascii=False)
    dj, tok = ai.chat_json(CAST_INTRO_SYS, user, tok=tok, max_tokens=700)

    adir = C.APP / "assets" / eid / "audio" / "cast"
    itext, iwords, tok = voice.voice_multi(dj.get("intro", ""), adir, key, langs, "narrator", tok)
    audio = {lg: f"assets/{eid}/audio/cast/{key}_{lg}.mp3" for lg in langs}
    scene = {"id": f"intro_{key}", "type": "hero", "mood": mood,
             "art": f"assets/{eid}/cast/{key}.png", "name": ent["display_name"],
             "epithets": dj.get("epithets", []), "legend": dj.get("legend_line", ""), "era": era,
             "lines": [{"type": "narration", "role": "narrator", "text": itext, "audio": audio,
                        "words": iwords}]}
    man["panels"] = [p for p in man["panels"] if p.get("id") != f"intro_{key}"]
    idx = next((i for i, p in enumerate(man["panels"]) if p["id"] == after_pid), len(man["panels"]) - 1)
    man["panels"].insert(idx + 1, scene)
    C.save_json(pj, man)
    print(f"  inserted cast intro 'intro_{key}' after {after_pid} ({len(man['panels'])} scenes)",
          flush=True)
    return tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eid")
    ap.add_argument("--langs", nargs="*", default=["en"])
    a = ap.parse_args()
    ep = C.find_episode(a.eid)
    build_intro(ep["id"] if ep else a.eid, langs=a.langs)
    ap.add_argument("--langs", nargs="*", default=["en"])
    a = ap.parse_args()
    ep = C.find_episode(a.eid)
    build_intro(ep["id"] if ep else a.eid, langs=a.langs)


if __name__ == "__main__":
    main()
