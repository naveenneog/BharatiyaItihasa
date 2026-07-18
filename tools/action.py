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
        f"this dynamic action pose: {action_desc}. Isolated on a plain SOLID FLAT uniform light-grey "
        f"studio background with NO texture, NO clouds, NO gradient, NO scenery, NO ground and NO "
        f"shadow — only the single character with clean sharp edges.",
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figure", default=DEMO["figure"])
    ap.add_argument("--bg", default=DEMO["bg"])
    ap.add_argument("--action", default=DEMO["action"])
    ap.add_argument("--narration", default=DEMO["narration"])
    a = ap.parse_args()
    build_action(a.figure, a.bg, a.action, a.narration)


if __name__ == "__main__":
    main()
