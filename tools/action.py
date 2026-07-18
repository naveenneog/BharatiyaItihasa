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
    words = voice.Synth().say(narration, amp3, voice.NARR["en"], voice.RATE["narrator"])

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


def add_action_beat(eid, after_pid, figure, bg_desc, action_desc, narration, key="a1", tok=None):
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

    print(f"  beat {key}: bg plate", flush=True)
    bg = d / "bg.png"
    tok = ai.gen_image(f"{sb.HOUSE_LOOK}\n\nWIDE CINEMATIC BACKGROUND SCENERY ONLY \u2014 no people, "
                       f"no characters, an empty stage: {bg_desc}", bg, tok, size="1536x1024")
    print(f"  beat {key}: character pose", flush=True)
    rawc = d / "char_raw.png"
    tok = ai.edit_image(CHAR_PROMPT.format(look=sb.HOUSE_LOOK, name=ent["display_name"],
                                           ref=ent["ref_desc"], act=action_desc),
                        [C.APP / ent["sheet"]], rawc, tok, size="1024x1024")
    char = d / "char.png"
    sz = matte.cutout(rawc, char)
    print(f"  beat {key}: matted {sz}", flush=True)

    adir = C.APP / "assets" / eid / "audio" / "en"
    adir.mkdir(parents=True, exist_ok=True)
    mp3 = adir / f"action_{key}.mp3"
    words = voice.Synth().say(narration, mp3, voice.NARR["en"], voice.RATE["narrator"])

    scene = {"id": f"action_{key}", "type": "action",
             "bg": f"assets/{eid}/action_{key}/bg.png", "char": f"assets/{eid}/action_{key}/char.png",
             "motion": {"fromX": -46, "toX": 4, "fromScale": 0.80, "toScale": 1.16,
                        "rot": -3, "dur": 7200, "bgZoom": 1.14, "bgPan": -7},
             "lines": [{"type": "narration", "role": "narrator", "text": {"en": narration},
                        "audio": {"en": f"assets/{eid}/audio/en/action_{key}.mp3"},
                        "words": {"en": words}}]}
    idx = next((i for i, p in enumerate(man["panels"]) if p["id"] == after_pid), len(man["panels"]) - 1)
    man["panels"].insert(idx + 1, scene)
    C.save_json(pj, man)
    print(f"  inserted action beat 'action_{key}' after {after_pid} ({len(man['panels'])} scenes)", flush=True)
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
    a = ap.parse_args()
    if a.beat:
        add_action_beat(a.beat, a.after, a.figure, a.bg, a.action, a.narration, key=a.key)
    else:
        build_action(a.figure, a.bg, a.action, a.narration)


if __name__ == "__main__":
    main()
