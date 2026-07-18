# CHANGELOG — Bhāratīya Itihāsa (Indian History)

A running decision + work log so work is traceable and we avoid re-solving the same
problems. Newest first.

---

## 2026-07-18 — Art direction DECIDED: anime/manga graphic-novel + character consistency

**Decision (resolves ROADMAP §9.2 / CONTEXT §7.2 "art direction"):** the app's visual
identity is a **shonen-manga / action-anime graphic novel** ("Naruto-style" dynamic action
choreography + comic dialogue), **not** the period-heritage or shadow-puppet options
previously floated. Requested by @naveenneog: *"build Indian history through the lens of
graphical storytelling, creating each character and maintaining character consistency, with
comic / mainly Naruto or anime style action and dialogue writing."*

Historical integrity is preserved *within* the anime idiom: era-accurate costume, weapons,
architecture and geography (grounded in each episode's `sources[]`); valour without gore;
neutral, unifying tone. Anime is the *rendering style*, not a license to fictionalise.

**Character consistency — the core new capability.** The Indian Tales engine renders every
illustration independently from text (consistency is textual-only via a `style_addendum`),
which is too weak for recognisable recurring heroes. New mechanism:

1. **Character registry** — each historical figure gets a canonical **character bible**
   (`characters/<slug>.json`: era-accurate face, hair, build, costume, signature weapon/prop,
   colour palette) authored once by gpt-4o from the figure/era/region + sources.
2. **Model sheet** — a full-body anime **reference sheet** (`app/assets/_characters/<slug>/sheet.png`)
   is generated once per figure from that bible.
3. **Reference-driven panels** — every story panel is rendered with gpt-image-2's
   **`images/edits`** endpoint, feeding the figure's model sheet(s) as the reference image, so
   face + costume + weapon stay identical across dynamic action panels and across episodes.

**Probe (VERIFIED this session):** `images/edits` on the `gpt-image-2` deployment
(`ai-contosohub530569751908`, api-version `2025-04-01-preview`) accepts multipart
`image[]` reference(s) + `prompt` and returns a consistent character. Test: generated a warrior-
queen model sheet, then edited it into a leaping Naruto-style action pose — braid+gold-clasp,
crimson-gold armor, jewelry, bracers, boots and talwar all held identical while pose/camera/
speed-lines changed. Auth = `Bearer <AAD token>` (`az account get-access-token --resource
https://cognitiveservices.azure.com`). Each high-quality 1024² call ≈ 120–135 s → **keep the
`keepactive` guard running** for all generation.

**Dialogue / speech bubbles — as a data overlay, not baked pixels.** Panels are generated with
**no text** (clean art). Dialogue + captions are authored as structured data and composited as
speech bubbles / caption boxes with Pillow. Rationale: crisp lettering, and the same panel art
is reused across all 6 languages (only the bubble layer is re-lettered) — a big win for the
multilingual app and for later narration.

**Engine (new `tools/`, adapted from IndianTales):**
- `tools/style_bible.py` — shonen-manga style bible + panel/camera/action + bubble conventions.
- `tools/gen_character.py` — design (gpt-4o) + render (gpt-image-2) a character model sheet;
  maintains `characters/registry.json`.
- `tools/comic_engine.py` — author a comic storyboard (panels + dialogue) referencing registry
  characters, render each panel via `images/edits` (consistency), composite bubbles → comic pages.

Kept compatible with the existing publish/narration pipeline so 6-language TTS + the PWA reader
+ Firebase deploy can be layered on in Phase 1 without re-architecting.
