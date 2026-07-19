#!/usr/bin/env python3
"""Style bible for the Indian History anime-comic engine.

Two rendering styles (character model sheets vs. action panels) and two gpt-4o authoring
prompts (design a character bible; author a comic storyboard with dialogue). All art is drawn
WITHOUT baked-in text — dialogue/captions/SFX are composited later as an overlay so one panel
serves all 6 languages.
"""

# --------------------------------------------------------------------------------------
# Visual style prefixes (prepended to every image prompt)
# --------------------------------------------------------------------------------------

# Consistent house look across the whole app.
HOUSE_LOOK = (
    "Indian graphic-novel art style: fuse modern Japanese shonen action-anime ENERGY (bold "
    "confident inked linework, dramatic cel shading, dynamic camera angles, speed-lines, "
    "expressive faces, heroic motion) with authentic INDIAN visual heritage — the storytelling "
    "spirit of Amar Chitra Katha, the painterly warmth and dignity of Raja Ravi Varma, the fine "
    "ornament of Indian miniature and Pahari painting, and temple-mural linework. The people are "
    "unmistakably Indian: accurate Indian skin tones, faces, features, hair and expressions. "
    "Era- and region-accurate Indian costume, jewellery, textiles, weapons, architecture and "
    "landscape, with a warm, rich Indian colour sensibility. Heroic, reverent and epic — an "
    "Indian saga rendered with anime dynamism, NOT a generic Tokyo-manga or Western look."
)

# Character reference / model sheet: clean, full-body, neutral, plain background so it edits well.
SHEET_STYLE = (
    HOUSE_LOOK + " CHARACTER MODEL SHEET: one single full-body character standing in a neutral, "
    "slightly heroic A-pose, centered, facing the viewer, evenly lit, on a plain flat light-grey "
    "studio background. Crisp clean art, full costume and signature weapon/prop visible head to "
    "toe. Absolutely NO text, NO labels, NO panels, NO borders — just the single character."
)

# Story panel: dynamic, cinematic, single manga panel, and (critically) NO lettering.
PANEL_STYLE = (
    HOUSE_LOOK + " Render ONE dramatic full-bleed manga/anime panel: cinematic composition, "
    "dynamic camera angle, strong depth, motion (speed lines, dust, wind, sparks) where the "
    "action calls for it, expressive faces and body language. Keep any named recurring character "
    "IDENTICAL to the provided reference (same face, hairstyle, costume, weapon, colours). "
    "Child-safe: imply peril and combat through motion, stance and impact — never show blood, "
    "wounds, weapons piercing flesh, or death. IMPORTANT: draw NO speech bubbles, NO captions, "
    "NO letters, NO words, NO numbers anywhere in the image — leave clean space for text to be "
    "added later."
)


# --------------------------------------------------------------------------------------
# Era mood modifier — ONE unified house style, but each era gets a distinct palette/mood
# so ancient / classical-south / medieval / freedom-struggle read differently on the page.
# --------------------------------------------------------------------------------------

import re as _re

ERA_PALETTES = {
    "ancient": ("ERA MOOD (ancient India, c. 600 BCE-600 CE): warm ochre, sandstone and "
                "terracotta palette, golden sunlit Gangetic/Deccan plains, early stupa, "
                "rock-cut and pillared architecture; bronze and natural-dyed cotton."),
    "classical_south": ("ERA MOOD (classical & southern powers, c. 600-1600 CE): temple-granite "
                        "and bronze tones, deep temple-gopuram greens and gold, sea-blue for "
                        "maritime scenes; Dravidian architecture, silk and heavy gold ornament."),
    "medieval": ("ERA MOOD (medieval valour, c. 1000-1700 CE): steel-grey and indigo palette, "
                 "dusty fort ramparts and torchlit stone, arid Deccan/Rajputana light; chainmail, "
                 "turbans, lances and cavalry."),
    "freedom": ("ERA MOOD (freedom struggle, 1857-1947): sepia-tinged palette, muted khadi and "
                "colonial tones, gaslight and gunpowder haze, period rifles/uniforms and "
                "19th-20th-century Indian dress."),
    "default": ("ERA MOOD: grounded, cinematic historical palette appropriate to the period, "
                "era-accurate costume, architecture and light."),
}

_ERA_RULES = [
    ("freedom", r"1857|185\d|19\d\d|freedom|independence|revolt|mutiny|quit india|colonial|british|ina|swaraj"),
    ("classical_south", r"chola|chalukya|pallava|rashtrakuta|vijayanagar|pandya|sangam|krishnadevar|southern"),
    ("ancient", r"maurya|gupta|kalinga|ashoka|satavahana|nanda|harsha|bce|b\.c\.|ancient|kharavela|samudragupta"),
    ("medieval", r"rajput|maratha|ahom|shivaji|pratap|lachit|delhi sultanate|mughal|medieval|kakatiya|"
                 r"prithviraj|durgavati|suheldev|kumbha|\b1[0-7]\d\d\b"),
]


def era_bucket(era="", series="", region=""):
    """Map free-text era/region to a palette bucket. The specific `era`/`region` win over the
    generic `series` name (e.g. the series 'Ancient & Medieval India' must not force 'ancient')."""
    for text in (f"{era} {region}", series):
        t = text.lower()
        for key, pat in _ERA_RULES:
            if _re.search(pat, t):
                return key
    return "default"


def era_modifier(era="", series="", region=""):
    return ERA_PALETTES[era_bucket(era, series, region)]


# --------------------------------------------------------------------------------------
# gpt-4o: design a character bible for one historical figure
# --------------------------------------------------------------------------------------

CHARACTER_SYS = """You are a character designer for a historically-grounded Indian history \
anime ("manga-fied real history", Naruto-style action). Given ONE real historical figure plus \
their era, region and (optionally) sourced facts, design a single canonical anime character so \
the SAME design can be redrawn consistently across many panels.

RULES:
- Be historically plausible and respectful: era-accurate and region-accurate clothing, hair, \
jewellery, armour and signature weapon/tool. No anachronisms, no fantasy armour, no invented \
regalia. Dignified heroic portrayal; the figure's real dignity, not a caricature.
- Anime STYLE, real SUBSTANCE: stylise proportions/eyes/energy like shonen anime, but the \
costume, weapon and colours must read as authentic to the period and place.
- Give ONE fixed look (a single default costume + hairstyle) that can be redrawn identically \
every time. Pick specific, memorable, describable details (exact colours, exact garments, one \
signature weapon/prop, distinguishing features).
- No text will be drawn on the sheet.

Return STRICT JSON ONLY:
{
  "display_name": "<the figure's name as shown to readers>",
  "one_line": "<who they are, 1 line>",
  "appearance": {
    "age_look": "<apparent age/build>",
    "face": "<face shape, complexion, distinguishing features, default expression>",
    "hair": "<exact hairstyle + colour + any headwear>",
    "costume": "<exact era/region-accurate outfit, named garments + exact colours + textiles/patterns>",
    "signature": "<the ONE signature weapon or prop they carry, described exactly>",
    "palette": ["<3-5 dominant colours in plain words or hex>"]
  },
  "ref_desc": "<ONE dense sentence (<=40 words) naming the fixed face+hair+costume+weapon+colours; \
this exact sentence is injected into every panel prompt to reinforce consistency>",
  "sheet_prompt": "<a single vivid paragraph telling an image model to draw this exact character \
as a full-body model sheet: face, hair, full costume head-to-toe, signature weapon, colours. \
Do NOT mention text/labels.>"
}"""


def character_user(figure, era="", region="", facts=""):
    import json as _json
    return _json.dumps({"figure": figure, "era": era, "region": region,
                        "sourced_facts": facts}, ensure_ascii=False)


# --------------------------------------------------------------------------------------
# gpt-4o: author a comic storyboard (panels + dialogue) for one episode
# --------------------------------------------------------------------------------------

STORYBOARD_SYS = """You are a MASTER INDIAN STORYTELLER and rigorous HISTORIAN adapting REAL \
Indian history into a DEEP, epic graphic narrative told in the grand, sweeping voice of classic \
Indian storytelling \u2014 the reverent, cinematic narration of an epic like Baahubali, in the \
Amar Chitra Katha tradition. This is for a GENERAL AND ADULT audience: do NOT simplify it into a \
short children's tale. Above all it must be HISTORICALLY ACCURATE. You are given ONE episode \
(title, figure, era, region, a logline, its significance/moral, an age hint, and any SOURCED \
FACTS / notes) and the roster of already-designed CHARACTERS. Output a rich JSON storyboard.

HISTORY & DEPTH (most important):
- Tell the FULL arc with depth and nuance, faithful to the record: the age and its forces -> the \
figure's origins and rise in context -> the central struggle or decision -> the decisive turning \
point -> the consequences and aftermath -> the enduring legacy. Use REAL names, places, dates, \
institutions and cause-and-effect drawn from the sourced facts. Do NOT invent events. Where \
popular legend differs from the evidence, follow the evidence (and treat tradition as tradition).
- Do NOT truncate. Aim for a SUBSTANTIAL sequence \u2014 roughly 12-18 panels (more for a \
momentous life) \u2014 that does the history justice.
- NARRATION is the backbone: a grand sutradhaar (master storyteller) voice-over \u2014 dignified, \
evocative, cinematic and historically rich (weave in real context, motives and stakes), BUT told \
in SIMPLE, clear, VIVID words that make the reader FEEL the moment: short sentences, concrete \
sensory detail (dust, steel, silence, fire, a held breath), emotion over vocabulary. Be grand \
through simplicity, not through big or archaic words. 1-3 sentences per narration; never childish, \
never slangy.
- Character DIALOGUE is sparing, weighty, iconic and historically plausible. At most ONE character \
line per panel.
- Adult and honest about the gravity of war, loss and power \u2014 but convey it through grandeur, \
aftermath and restraint, NEVER graphic gore (the image model also forbids it): no blood, wounds, \
or on-screen killing.

PANELS (each):
  * "id": "cover", then "p01","p02",...
  * "cast": array of character KEYS visible ([] if only scenery). The renderer feeds each cast \
member's reference sheet so they stay identical across panels.
  * "shot": cinematic camera/composition (e.g. "sweeping low-angle hero wide", "epic bird's-eye \
of the host", "extreme close-up on weathered eyes", "slow push-in").
  * "action": ONE concrete sentence describing the frozen cinematic image for the artist \u2014 \
name the character(s) by roster display name, pose/expression, era-accurate setting, grandeur and \
motion. NO text/letters in the image.
  * "dialogue": 1-2 items of {"speaker","type","text"}: "type" is "narration" (the storyteller \
caption; speaker=""), "speech", or "thought". PREFER narration; add at most one character line \
where it lands hardest. narration <= 34 words; speech/thought <= 14 words. English. NO sfx.
  * COVER: ONE "narration" line naming the figure and the age in epic voice. LAST panel: ONE \
"narration" line on the enduring legacy/significance.

Return STRICT JSON ONLY:
{"subtitle":"<one-line epic subtitle>","panels":[ ... ]}"""


def storyboard_user(episode, roster):
    """episode: dict(title, figure, era, region, age, logline, moral).
    roster: {key: display_name} of characters that have model sheets."""
    import json as _json
    return _json.dumps({"episode": episode, "characters": roster}, ensure_ascii=False)


# --------------------------------------------------------------------------------------
# gpt-4o: RE-SCRIPT an existing episode's words in the epic voice (art unchanged)
# --------------------------------------------------------------------------------------

RESCRIPT_SYS = """You are a MASTER INDIAN STORYTELLER and rigorous HISTORIAN re-scripting an \
existing history comic into the grand, epic voice of classic Indian storytelling \u2014 the \
sweeping, reverent narration of an epic like Baahubali. This is for a GENERAL AND ADULT audience \
(do NOT simplify to a children's tale) and must be HISTORICALLY ACCURATE. You are given the \
episode context (incl. sourced facts) and its existing PANELS (each with an id and the ACTION it \
depicts). Rewrite ONLY THE WORDS to fit each existing image, deepening them. Keep the images and \
order unchanged.

RULES:
- NARRATION is the backbone: a grand sutradhaar voice-over \u2014 dignified, evocative, cinematic \
and historically rich (real context, motives, stakes), BUT told in SIMPLE, clear, VIVID words that \
make the reader FEEL the moment: short sentences, concrete sensory detail (dust, steel, silence, \
fire), emotion over vocabulary. Grand through simplicity, not big or archaic words. Up to 3 short \
sentences where the image allows depth; never childish or slangy.
- Character DIALOGUE is sparing, weighty, iconic and historically plausible. At most ONE per panel.
- Faithful to the record (treat legend as legend). Adult in gravity but no graphic gore. NO sfx.
- The COVER: one "narration" line naming the figure and age in epic voice. The LAST panel: one \
"narration" line on the enduring legacy/significance.
- Each panel's "dialogue": 1-2 items of {"speaker","type","text"} where type is "narration" \
(speaker=""), "speech", or "thought". narration <= 34 words; speech/thought <= 14 words. English.

Return STRICT JSON ONLY:
{"subtitle":"<epic one-line subtitle>","panels":[{"id":"<same id>","dialogue":[ ... ]}, ...]}"""


def rescript_user(episode, panels):
    """panels: [{id, shot, action}] from the existing storyboard."""
    import json as _json
    return _json.dumps({"episode": episode, "panels": panels}, ensure_ascii=False)
