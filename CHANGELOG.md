# CHANGELOG — Bhāratīya Itihāsa (Indian History)

A running decision + work log so work is traceable and we avoid re-solving the same
problems. Newest first.

---

## 2026-07-18 (later 2) — Indian-adapted style + 6-language comics

**Two requests from @naveenneog:** *"even though it's an anime theme, make it adapted to Indian"*
and *"we also want for Indian languages also."*

**Indian-adapted art:** rewrote `style_bible.HOUSE_LOOK` from generic Tokyo-manga to an **Indian
graphic-novel fusion** — shonen-anime energy rooted in Indian visual heritage (Amar Chitra Katha,
Raja Ravi Varma, miniature/temple art), authentic Indian faces/skin/costume. Propagates to both
the model-sheet and panel prompts.

**Multilingual (6 languages en/kn/hi/ta/te/de):** because the panel art is generated **text-free**,
languages are just a re-lettering pass:
- `translate.py` — gpt-4o translates dialogue+captions+title into each language (native script),
  stored as an `i18n` map on the saved storyboard; already-translated languages are skipped.
- `weblettering.py` — switched the letterer from Pillow to **Chromium/HTML**. PIL can't shape
  Indic scripts (no libraqm: `features.check('raqm')` = False), but Chromium shapes Devanagari /
  Kannada / Tamil / Telugu correctly via HarfBuzz using system **Nirmala UI**. Renders one comic
  page per language (CSS bubbles/shouts/thoughts, caption bars, star-burst SFX, per-language title).
- `comic_engine.py` now: render text-free art → translate → render `app/comics/<id>/<lang>.jpg`
  for every language; `--reletter` re-does translation (cached) + all language pages with no image
  gen; new `--langs` flag. Removed the old Pillow `lettering.py` (superseded).

**Verified:** re-lettered the existing Ashoka art into all 6 languages with zero image
regeneration — Hindi/Tamil/Telugu (and Kannada/German/English) all shape correctly, including
inside shout/thought bubbles. Output dir per episode: `app/comics/<id>/{en,kn,hi,ta,te,de}.jpg`.

**Note:** SFX remain Latin (universal onomatopoeia) for now; localising them is a future polish.

---

## 2026-07-18 (later) — Anime-comic engine BUILT + verified on 3 eras

Implemented the full character-consistent engine in `tools/` (see CONTEXT §0A):
`aiclient.py`, `style_bible.py` (house style + `era_modifier`), `lettering.py`, `common.py`
(character registry + collection loader), `gen_character.py`, `comic_engine.py`. Committed as
granular per-feature commits.

**Verified end-to-end on three eras** (character stays identical across all panels via the
model-sheet→`images/edits` reference mechanism):
- **Rani Lakshmibai** (freedom, 1858) — 4-panel sample, the first approval.
- **Chhatrapati Shivaji** (medieval, 1666) — full 7-panel story "Shivaji's Quiet Escape from
  Agra"; medieval palette; correctly labels the basket-escape as *tradition*.
- **Emperor Ashoka** (ancient, 261 BCE) — ancient palette validation.

**Lettering fix:** on panels with a top narration caption + a speech bubble, the two collided and
clipped text. Bubbles now reserve the caption/narration vertical bands and stack in the free
space; `compose_page` centers a short final row. Added a **`--reletter`** path that re-runs
lettering from the saved storyboard + existing art with no API cost (used to fix the Shivaji page
without re-generating it).

**Design choices worth keeping:** (1) art is generated **text-free** and dialogue is a Pillow
overlay → one panel serves all 6 languages later; (2) one **unified house style** + per-era
palette (not a different style per era) for brand + consistency; (3) a **character registry** so a
figure designed once is reused (identical) across every episode.

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
