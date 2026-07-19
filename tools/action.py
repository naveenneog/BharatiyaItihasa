#!/usr/bin/env python3
"""Action-sequence generator: a background scenery plate + a transparent character cut-out that
is animated OVER the background (enter, charge/leap, scale) with voiced narration.

gpt-image-2 has no transparent background, so the character is drawn on a flat background and
matted out (tools/matte.py). Writes app/data/<id>.action.json for player/action.html.

  cd tools; $env:PYTHONIOENCODING="utf-8"; python action.py            # builds the demo scene
"""
import argparse, sys
sys.stdout.reconfigure(encoding="utf-8")
import aiclient as ai
import style_bible as sb
import common as C
import gen_character as gc
import matte
import voice

# a marquee demo: Rani Lakshmibai charging at Gwalior
DEMO = {
    "figure": "Rani Lakshmibai of Jhansi",
    "bg": ("a vast dusty Bundelkhand battlefield plain at golden dusk before the hill-fort of "
           "Gwalior, distant ramparts and banners silhouetted, swirling dust and low sun, dramatic "
           "sky, empty foreground"),
    "action": ("mid-charge, leaning forward with her talwar raised high, cape and braid streaming "
               "behind her, fierce determined expression, full body, angled to the right as if "
               "surging across the field"),
    "narration": ("And so, when Jhansi had fallen and hope itself seemed lost, the Rani of Jhansi "
                  "turned her horse toward Gwalior and charged headlong into legend."),
}


def build_action(figure, bg_desc, action_desc, narration, out_id=None, tok=None):
    tok = tok or ai.token()
    ent, tok = gc.ensure_character(figure, tok=tok)
    aid = out_id or f"action_{C.slug(figure)}"
    d = C.APP / "assets" / aid / "action"
    d.mkdir(parents=True, exist_ok=True)

    print("  bg plate", flush=True)
    bg = d / "bg.png"
    tok = ai.gen_image(f"{sb.HOUSE_LOOK}\n\nWIDE CINEMATIC BACKGROUND SCENERY ONLY — no people, "
                       f"no characters, an empty stage: {bg_desc}", bg, tok, size="1536x1024")

    print("  character action pose", flush=True)
    rawc = d / "char_raw.png"
    tok = ai.edit_image(
        f"{sb.HOUSE_LOOK}\n\nDraw ONLY {ent['display_name']} ({ent['ref_desc']}) at FULL LENGTH in "
        f"this dynamic action pose: {action_desc}. The WHOLE figure must be fully inside the frame "
        f"with a clear even margin of empty background on every side, NOT touching any edge. Isolated "
        f"on a plain SOLID FLAT perfectly uniform light-grey studio background with NO texture, NO "
        f"clouds, NO gradient, NO scenery, NO ground and NO shadow — only the single character with "
        f"clean sharp edges.",
        [C.APP / ent["sheet"]], rawc, tok, size="1024x1024")
    char = d / "char.png"
    sz = matte.cutout(rawc, char)
    print(f"  matted cut-out {sz}", flush=True)

    print("  narration voice", flush=True)
    adir = C.APP / "assets" / aid / "audio"
    adir.mkdir(parents=True, exist_ok=True)
    amp3 = adir / "action_en.mp3"
    v, rate = voice.voice_for("narrator", "en")
    words = voice.Synth().say(narration, amp3, v, rate)

    manifest = {
        "id": aid, "figure": figure, "title": ent["display_name"],
        "bg": f"assets/{aid}/action/bg.png", "char": f"assets/{aid}/action/char.png",
        "charSize": sz,
        "motion": {"fromX": -46, "toX": 4, "fromScale": 0.80, "toScale": 1.16,
                   "rot": -3, "dur": 6800, "bgZoom": 1.14, "bgPan": -7},
        "narration": {"text": narration, "audio": f"assets/{aid}/audio/action_en.mp3", "words": words},
    }
    C.save_json(C.APP / "data" / f"{aid}.action.json", manifest)
    print(f"DONE action -> {aid}.action.json", flush=True)
    return manifest


CHAR_PROMPT = (
    "{look}\n\nDraw ONLY {name} ({ref}) at FULL LENGTH in this dynamic action pose: {act}. The "
    "WHOLE figure must be fully inside the frame with a clear even margin of empty background on "
    "every side, NOT touching any edge. Isolated on a plain SOLID FLAT perfectly uniform light-grey "
    "studio background with NO texture, NO clouds, NO gradient, NO scenery, NO ground and NO shadow "
    "\u2014 only the single character with clean sharp edges.")


def add_action_beat(eid, after_pid, figure, bg_desc, action_desc, narration, key="a1",
                    langs=("en",), reuse=True, tok=None):
    """Generate an action scene and INSERT it into <eid>.player.json after panel `after_pid`, so a
    voiced motion-comic drops into an animated action shot mid-story. Needs voice.py run first."""
    pj = C.APP / "data" / f"{eid}.player.json"
    man = C.load_json(pj, None)
    if not man:
        raise SystemExit(f"no player manifest for {eid} (run: python voice.py {eid} --langs en)")
    tok = tok or ai.token()
    ent, tok = gc.ensure_character(figure, tok=tok)
    d = C.APP / "assets" / eid / f"action_{key}"
    d.mkdir(parents=True, exist_ok=True)

    bg = d / "bg.png"
    if not (reuse and bg.exists()):
        print(f"  beat {key}: bg plate", flush=True)
        tok = ai.gen_image(f"{sb.HOUSE_LOOK}\n\nWIDE CINEMATIC BACKGROUND SCENERY ONLY \u2014 no "
                           f"people, no characters, an empty stage: {bg_desc}", bg, tok, size="1536x1024")
    char = d / "char.png"
    if not (reuse and char.exists()):
        print(f"  beat {key}: character pose", flush=True)
        rawc = d / "char_raw.png"
        tok = ai.edit_image(CHAR_PROMPT.format(look=sb.HOUSE_LOOK, name=ent["display_name"],
                                               ref=ent["ref_desc"], act=action_desc),
                            [C.APP / ent["sheet"]], rawc, tok, size="1024x1024")
        print(f"  beat {key}: matted {matte.cutout(rawc, char)}", flush=True)

    adir = C.APP / "assets" / eid / "audio" / "action"
    text_map, words_map, tok = voice.voice_multi(narration, adir, f"action_{key}", langs, "narrator", tok)
    audio = {lg: f"assets/{eid}/audio/action/action_{key}_{lg}.mp3" for lg in langs}

    scene = {"id": f"action_{key}", "type": "action", "mood": "battle",
             "bg": f"assets/{eid}/action_{key}/bg.png", "char": f"assets/{eid}/action_{key}/char.png",
             "motion": {"fromX": -46, "toX": 4, "fromScale": 0.80, "toScale": 1.16,
                        "rot": -3, "dur": 7200, "bgZoom": 1.14, "bgPan": -7},
             "lines": [{"type": "narration", "role": "narrator", "text": text_map,
                        "audio": audio, "words": words_map}]}
    idx = next((i for i, p in enumerate(man["panels"]) if p["id"] == after_pid), len(man["panels"]) - 1)
    man["panels"] = [p for p in man["panels"] if p.get("id") != f"action_{key}"]
    idx = next((i for i, p in enumerate(man["panels"]) if p["id"] == after_pid), len(man["panels"]) - 1)
    man["panels"].insert(idx + 1, scene)
    C.save_json(pj, man)
    print(f"  inserted action beat 'action_{key}' after {after_pid} ({len(man['panels'])} scenes)", flush=True)
    return tok


NO_TEXT = ("Absolutely NO text, NO speech bubbles, NO captions, NO name plates, NO letters, NO "
           "words, NO numbers and NO written banners anywhere in the image.")


STILL_PROMPT = (
    "{look}\n\nDraw ONLY {name} ({ref}) at FULL LENGTH standing in this calm, STILL, weightless "
    "pose: {act}. The WHOLE figure must be fully inside the frame with a clear even margin of empty "
    "background on every side, NOT touching any edge. Isolated on a plain SOLID FLAT perfectly "
    "uniform light-grey studio background with NO texture, NO clouds, NO gradient, NO scenery, NO "
    "ground and NO shadow \u2014 only the single character with clean sharp edges.")


def add_multi_beat(eid, after_pid, bg_desc, narration, cast, key="m1", langs=("en",), reuse=True,
                   tok=None, mood="battle", scene_motion=None, bg_people=False, replace_pid=None):
    """Insert (or replace) a MULTI-character action scene: several consistent cut-outs animated over
    one background plate. cast = [{figure, action, era?, region?, facts?, motion, slug?, reuse_img?,
    still?, spirit?}]. `still` uses a calm/serene pose prompt; `spirit` flags the cut-out for the
    player's ethereal fade-and-rise style. `mood` sets the scene/music mood; `scene_motion` overrides
    the bg motion; `bg_people` lets the plate hold distant background figures; `replace_pid` swaps
    that panel in place instead of inserting after `after_pid`. voice.py must be run first."""
    pj = C.APP / "data" / f"{eid}.player.json"
    man = C.load_json(pj, None)
    if not man:
        raise SystemExit(f"no player manifest for {eid} (run: python voice.py {eid} --langs en)")
    tok = tok or ai.token()
    d = C.APP / "assets" / eid / f"action_{key}"
    d.mkdir(parents=True, exist_ok=True)

    bg = d / "bg.png"
    if not (reuse and bg.exists()):
        print(f"  {key}: bg plate", flush=True)
        stage = ("WIDE CINEMATIC BACKGROUND SCENERY with NO central hero \u2014 only small, faraway "
                 "background figures at most" if bg_people else
                 "WIDE CINEMATIC BACKGROUND SCENERY ONLY \u2014 no people, no characters, an empty stage")
        tok = ai.gen_image(f"{sb.HOUSE_LOOK}\n\n{stage}: {bg_desc}. {NO_TEXT}", bg, tok, size="1536x1024")

    chars = []
    for i, c in enumerate(cast):
        slug = c.get("slug", f"char{i}")
        if c.get("reuse_img"):
            cd = {"img": c["reuse_img"], "motion": c.get("motion", {})}
            if c.get("spirit"):
                cd["spirit"] = True
            chars.append(cd)
            continue
        ent, tok = gc.ensure_character(c["figure"], c.get("era", ""), c.get("region", ""),
                                       c.get("facts", ""), tok=tok)
        cpng = d / f"{slug}.png"
        if not (reuse and cpng.exists()):
            print(f"  {key}: char {ent['display_name']} ({slug})", flush=True)
            raw = d / f"{slug}_raw.png"
            tmpl = STILL_PROMPT if c.get("still") else CHAR_PROMPT
            tok = ai.edit_image(tmpl.format(look=sb.HOUSE_LOOK, name=ent["display_name"],
                                            ref=ent["ref_desc"], act=c["action"]),
                                [C.APP / ent["sheet"]], raw, tok, size="1024x1024")
            print(f"    matted {matte.cutout(raw, cpng)}", flush=True)
        cd = {"img": f"assets/{eid}/action_{key}/{slug}.png", "motion": c.get("motion", {})}
        if c.get("spirit"):
            cd["spirit"] = True
        chars.append(cd)

    adir = C.APP / "assets" / eid / "audio" / "action"
    text_map, words_map, tok = voice.voice_multi(narration, adir, f"action_{key}", langs, "narrator", tok)
    audio = {lg: f"assets/{eid}/audio/action/action_{key}_{lg}.mp3" for lg in langs}

    scene = {"id": f"action_{key}", "type": "action", "mood": mood,
             "bg": f"assets/{eid}/action_{key}/bg.png", "chars": chars,
             "motion": scene_motion or {"bgZoom": 1.12, "bgPan": -6, "dur": 7200},
             "lines": [{"type": "narration", "role": "narrator", "text": text_map,
                        "audio": audio, "words": words_map}]}
    man["panels"] = [p for p in man["panels"] if p.get("id") != f"action_{key}"]
    if replace_pid:
        idx = next((i for i, p in enumerate(man["panels"]) if p["id"] == replace_pid), None)
        if idx is None:
            idx = next((i for i, p in enumerate(man["panels"]) if p["id"] == after_pid),
                       len(man["panels"]) - 1) + 1
        else:
            man["panels"].pop(idx)
        man["panels"].insert(idx, scene)
        where = f"replaced {replace_pid}"
    else:
        idx = next((i for i, p in enumerate(man["panels"]) if p["id"] == after_pid), len(man["panels"]) - 1)
        man["panels"].insert(idx + 1, scene)
        where = f"after {after_pid}"
    C.save_json(pj, man)
    print(f"  {where}: 'action_{key}' ({len(man['panels'])} scenes)", flush=True)
    return tok


def add_split_beat(eid, after_pid, narration, slices, key="s1", langs=("en",), reuse=True,
                   tok=None, mood="battle", size="1536x1024"):
    """Insert a DIAGONAL 3-CUT montage (manga triptych): three HORIZONTAL diagonal slices reveal in
    sequence, each its own richly illustrated WIDE panel, optionally carrying a battle-cry slogan.
    slices = [{figure?, fight?:bool, action, era?, region?, facts?, slogan?({en,hi}|str), pos?,
    zoom?}]. A slice with a `figure` keeps that character's identity (drawn from its model sheet); a
    `fight` slice is a free ensemble scene. Slices are landscape so faces + action read across the
    full width. voice.py must be run first."""
    pj = C.APP / "data" / f"{eid}.player.json"
    man = C.load_json(pj, None)
    if not man:
        raise SystemExit(f"no player manifest for {eid} (run: python voice.py {eid} --langs en)")
    tok = tok or ai.token()
    d = C.APP / "assets" / eid / f"split_{key}"
    d.mkdir(parents=True, exist_ok=True)

    out_slices = []
    for i, s in enumerate(slices):
        img = d / f"s{i}.png"
        if not (reuse and img.exists()):
            if s.get("fight") or not s.get("figure"):
                print(f"  split {key}: slice {i} (scene)", flush=True)
                tok = ai.gen_image(f"{sb.HOUSE_LOOK}\n\nDRAMATIC FULL-BLEED WIDE CINEMATIC KEY-ART, "
                                   f"the action filling the frame, dynamic angle: {s['action']}. "
                                   f"{NO_TEXT}", img, tok, size=size)
            else:
                ent, tok = gc.ensure_character(s["figure"], s.get("era", ""), s.get("region", ""),
                                               s.get("facts", ""), tok=tok)
                print(f"  split {key}: slice {i} ({ent['display_name']})", flush=True)
                tok = ai.edit_image(
                    f"{sb.HOUSE_LOOK}\n\nDRAMATIC WIDE CINEMATIC CHARACTER KEY-ART of "
                    f"{ent['display_name']} ({ent['ref_desc']}): {s['action']}. The character's FACE "
                    f"and upper body must be LARGE, centred and clearly visible; cinematic rim-light, "
                    f"a richly illustrated atmospheric background (NOT a plain studio background). "
                    f"{NO_TEXT}",
                    [C.APP / ent["sheet"]], img, tok, size=size)
        so = {"img": f"assets/{eid}/split_{key}/s{i}.png"}
        if s.get("slogan"):
            so["slogan"] = s["slogan"]
        if s.get("pos"):
            so["pos"] = s["pos"]
        if s.get("zoom"):
            so["zoom"] = s["zoom"]
        out_slices.append(so)

    adir = C.APP / "assets" / eid / "audio" / "split"
    text_map, words_map, tok = voice.voice_multi(narration, adir, f"split_{key}", langs, "narrator", tok)
    audio = {lg: f"assets/{eid}/audio/split/split_{key}_{lg}.mp3" for lg in langs}

    scene = {"id": f"split_{key}", "type": "split", "mood": mood, "slices": out_slices,
             "lines": [{"type": "narration", "role": "narrator", "text": text_map,
                        "audio": audio, "words": words_map}]}
    man["panels"] = [p for p in man["panels"] if p.get("id") != f"split_{key}"]
    idx = next((i for i, p in enumerate(man["panels"]) if p["id"] == after_pid), len(man["panels"]) - 1)
    man["panels"].insert(idx + 1, scene)
    C.save_json(pj, man)
    print(f"  inserted split 'split_{key}' after {after_pid} ({len(man['panels'])} scenes)", flush=True)
    return tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figure", default=DEMO["figure"])
    ap.add_argument("--bg", default=DEMO["bg"])
    ap.add_argument("--action", default=DEMO["action"])
    ap.add_argument("--narration", default=DEMO["narration"])
    ap.add_argument("--beat", metavar="EID", help="insert an action beat into episode EID's player.json")
    ap.add_argument("--after", default="cover", help="insert the beat after this panel id")
    ap.add_argument("--key", default="a1")
    ap.add_argument("--langs", nargs="*", default=["en"])
    a = ap.parse_args()
    if a.beat:
        add_action_beat(a.beat, a.after, a.figure, a.bg, a.action, a.narration, key=a.key, langs=a.langs)
    else:
        build_action(a.figure, a.bg, a.action, a.narration)


if __name__ == "__main__":
    main()
