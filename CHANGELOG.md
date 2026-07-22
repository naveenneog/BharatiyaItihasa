# CHANGELOG — Bhāratīya Itihāsa (Indian History)

A running decision + work log so work is traceable and we avoid re-solving the same
problems. Newest first.

---

## 2026-07-22 — 🌸 Gupta Golden Age COMPLETE (13/13) · voice fix · autonomous continuous build

- **The Gupta Golden Age chapter is COMPLETE (13/13, all QA-clean):** Chandragupta I, Samudragupta,
  Chandragupta II, Prabhavatigupta (regent queen), Faxian, Aryabhata, the birth of Zero (Brahmagupta),
  the Iron Pillar, Sushruta, Nalanda, Kalidasa, Gupta sculpture, Skandagupta. Innovation stories woven
  throughout (astronomy/zero, metallurgy, medicine, learning). Every story carries recent scholarship
  (pi as *asanna* not "proven irrational"; the 2017 Bakhshali dating rebuttal; iron-pillar phosphorus
  passive layer; Alchon-Hun numismatics; Nalanda's phased decline; the "golden age for whom?" nuance).
- **Voice fix — Sanskrit pronunciation:** `voice.py` now **de-accents English/IAST diacritics to plain
  ASCII** for the TTS (`Āryabhaṭa`→`Aryabhata`), leaving Hindi Devanagari intact; the 4 affected stories
  were re-voiced. Added **voice QA via `gpt-4o-transcribe`** (transcribe → compare → flag mispronounced
  names) to the QA loop.
- **Autonomous continuous build:** a chapter **queue + backlog + driver** now builds era after era
  unattended — Gupta → Maurya → Vijayanagara, then **self-extends** by researching + seeding the next
  backlog era when the queue runs low. Each chapter is deep and includes **social/scientific/economic/
  scholarly innovation** stories. Every cycle QAs each story (visual+audio+voice+emotional+regnal+
  accuracy) and **version-controls code + assets to GitHub** (main repo + `app/assets` masters submodule).
- **Assets** are a submodule (`bharatiya-itihasa-masters`), pushed in ≤600 MB chunks.

---

## 2026-07-21 — 🏛️ The Chola Empire chapter is COMPLETE (13/13)

All thirteen Chola stories are built and QA-clean (visual + audio + emotional + regnal), forming the
first deep, grouped **chapter** — rise, rule, heroes, wars, craft and the innovations of the age:

- **Rise/founder:** Vijayalaya Seizes Thanjavur; Taming the Kaveri (Grand Anicut irrigation).
- **Rule/self-governance:** The Village Chooses Its Guardians (Uttaramerur *Kudavolai* palm-leaf ballot);
  Kundavai (hospitals, temples, arts); Kulottunga (abolished tolls — *Sungam Tavirtta Cholan*).
- **Heroes/wars:** Rajaraja's Sword; Rajendra Brings the Ganges South; Rajendra's Fleet to Srivijaya (1025 CE).
- **Craft/faith/letters:** Rajaraja Raises Brihadisvara; The Shadow of the Great Vimana (temple engineering);
  Chola Bronze Artists; Tamil Merchant Guilds; Kamban Sings the Tamil Ramayana.

This session's new/redone Chola stories (Kundavai, Srivijaya, Kulottunga, Kamban + deepened Rajendra) each
carry **two animated action beats + a 3-band montage**, faces & action clear, emotional voice, regnal names
spoken as words. Vijayalaya + The Village Chooses Its Guardians are grandfathered from an earlier session
(one action beat + montage, 23/27 scenes) and QA-clean.

The 12-hour build continues into **breadth** (round-robin across eras) per the non-stop ask.

**Deployed to CDN (user-approved):** all **13** Chola stories are now live on
https://indian-history.web.app (was 5). `deploy/approved.json` `approved` = full Chola chapter; `publish.py`
re-encoded 363 images → WebP (176 MB, 981 files) and Firebase deploy released them. Live QA verified:
home manifest 13/13, every new story's manifest + WebP art + en/hi mp3 audio return 200.

---

## 2026-07-20 (later 3) — Deeper stories: 2 action beats, redo thin ones, 12h build

@naveenneog: "redo ones whose slides are less than 15, with actions and animations … next 12h
non-stop building the next stories … add more action scenes in a single story … do visual + audio
+ emotional QA for each story before marking it done."

- **Two action beats per story (was one)** — `grow.py` `BEATS_SYS`/`author_beats` now author **two**
  animated action beats at different dramatic moments (1st enters from the left, 2nd from the right)
  **plus** the climactic 3-band montage. `has_beats` recognises `action_auto` + `action_auto2` +
  `split_auto`. New + redone stories get the richer treatment; the 17 already-QA'd episodes
  (all ≥20 scenes) keep their single beat.
- **Redo the thin stories (<15 scenes)** — three were short: `ashoka` (11), `rajendra` (12),
  `shivaji` (12). Per-episode policy so hand-crafted flagship content is never lost:
  - **enrich** `rajendra` + `shivaji` — keep the bespoke storyboard **and co-star intro cards**
    (Mahipala / Aurangzeb + Hiroji), just add 2 action beats + a montage → 15 scenes.
  - **deep re-author** `ashoka` — genuinely thin narrative, no co-stars to lose, so re-author a
    longer storyboard (the generic deep author makes ~18–20 panels) + beats + montage.
  - New CLI: `grow.py --redo-thin [MIN]`, and single-episode `--enrich <eid>` / `--redo <eid>`
    for the QA gate to repair any short story without a full rebuild.
- **12h non-stop build** — one process now flows `--redo-thin → --chapter "The Chola Empire" →
  --breadth N`: fix the thin ones, finish the Chola chapter (Kundavai, Srivijaya fleet, Kulottunga,
  Kamban), then keep building more stories. Log: `<session>/files/build3.log`.
- **QA gate before "done"** — the every-2h monitor now enforces, per story: **≥15 scenes**, **2
  action beats + montage**, faces/action clear (band-crop rule, no baked captions), audio present
  (en+hi), **varied moods** (emotional), and **regnal names spoken as words**. Short/one-beat
  stories are auto-repaired with `--enrich`/`--redo` before being marked clean.
- **CDN hold** — `rajendra` is live on the CDN; it is redone locally and re-QA'd only. No CDN
  redeploy without explicit user OK (git commits remain auto-approved).

---

## 2026-07-20 (later 2) — Emotional voice, name pronunciation, mobile-friendly

@naveenneog: the hero speech felt robotic; names like "Rajaraja Chola I" were read as the letter
"I" not "the First"; and the stories should be mobile-friendly.

- **Emotional TTS** — narration + dialogue now carry emotion: an Azure `mstts:express-as` style plus
  a pitch/rate contour chosen from each scene's **mood** (battle / suspense / triumph / spirit /
  calm), with a plain-prosody fallback for voices that reject a style. Hindi **MAI voices are flaky
  with express-as** (0-byte turns), so they use pitch/rate emotion only. Mood is threaded through
  `voice_episode`, `voice_multi` (beats/intros) and the new re-voice path.
- **Regnal numerals spoken as words** — `voice._expand_regnal` turns "Rajaraja Chola I" into
  "Rajaraja Chola the First" (I→First … X→Tenth) for both audio and the on-screen line, while
  leaving the pronoun "I" ("When I…") alone.
- **`voice.revoice_manifest()`** — re-voices an episode **in place** (regenerates clips + word
  timings, updates the text) WITHOUT rebuilding the manifest, so montage/intro inserts survive.
  `voice.py <id> --revoice`. All built episodes re-voiced with emotion + the name fix.
- **Player is mobile-friendly** — controls stay visible on touch (they were hover-only), a ≤640px
  block scales narration/dialogue/hero-card/slogan fonts and the control bar (safe-area padding) and
  hides the long progress-dot strip; a portrait block lifts character cut-outs above the controls.
- **Cache-bust** — the player appends `?v=` to the manifest + audio URLs so re-voiced clips play
  fresh instead of a stale cached mp3 (this was why re-voiced audio first still sounded old).

---

## 2026-07-20 (later) — Animated breadth episodes + multi-episode arcs + timeline home page

@naveenneog: make the new episodes more animated (and show faces + actions clearly); build
multi-episode arcs for major subjects (Cholas — glory, craft, conquest, rule) not just single
episodes; and make the home page a three-era timeline.

- **Every episode is now animated** — `grow.py` gives each breadth episode a gpt-4o-authored
  **action beat** (hero cut-out striding/charging over era scenery) **and a 3-band montage**
  (hero + battle-cry / a wide scene / an action clash), on top of the hero+map intro and voiced
  story. Prompts enforce the **band-crop rule**: hero face clear in the top band, a WIDE scene in the
  middle band (no cropped faces), a clearly-lit action in the bottom band. A `--backfill-beats` pass
  adds these to the already-built episodes too.
- **Multi-episode arcs** — the corpus was already arc-structured; `SERIES_ARCS.md` now maps the
  arcs (Chola ×5, Maurya/Gupta, Rajput ×4, Maratha, Vijayanagara, Ahom, 1857, freedom struggle).
  Breadth now builds the **Chola arc first** (Rajaraja's temple, the merchant-guild seas, the bronze
  Nataraja, village self-government) then **round-robins the three series** so the Ancient, Medieval
  and Freedom-Struggle timelines all grow together instead of one era at a time.
- **Timeline home page** (`app/index.html`) — three collapsible era accordions (Ancient / Medieval /
  Freedom Struggle); each opens a chronological timeline of that era's heroes (year marker, dot,
  card with portrait/legend/EN+हिंदी). `tools/gallery.py` parses a year from each era and files it.
- Verified the animated beats on Mangal Pandey (action beat + montage, faces & action read clearly),
  0 JS errors.

---

## 2026-07-20 — Expand the collection: QA + Rani-level growth of other stories (12h run)

@naveenneog: do thorough visual QA and fix issues; expand the OTHER stories with everything we
learned from Rani; and start building the rest of the collection over the next ~12 hours.

- **Visual QA harness** — a Playwright capture that renders every panel of an episode through the
  real player (art + first-line lettering) and tiles them into contact sheets. Rani (27 scenes):
  **clean**, 0 JS errors, faces/actions read, no baked captions (only tasteful diegetic signage).
- **Hero portrait for the opening card** — `build_intro` now renders a dedicated face-forward hero
  portrait from the figure's model sheet (face centred, headroom for the title), like the co-star
  cards, instead of reusing the cover panel. Falls back to cover when there's no model sheet.
- **Bilingual STORY panels fix** — `voice_episode` only voices a language it finds translated in the
  storyboard, so episodes whose storyboard lacked Hindi got English-only story panels (while the
  beats, translated on the fly, were bilingual). The growth pipeline now **translates the storyboard
  to hi before voicing**, so story panels AND beats are both en+hi.
- **Rajendra Chola I → 12 scenes** (first expansion): voice en+hi, hero portrait + India-map intro,
  a real co-star intro (**Mahipala, the Pala king** struck by the Chola Ganges expedition c.1021
  CE), a **NAVAL fleet** action beat (a new setting vs cavalry), and a horizontal Ganga montage.
- **`grow.py` — 12-hour autonomous orchestrator**: applies the Rani recipe to the rest of the
  collection. Bespoke flagships (**Shivaji's escape from Agra** with Aurangzeb + Hiroji Farzand and
  an escape montage; **Ashoka's change of heart at Kalinga** with a war beat + a war→grief→dhamma
  montage), then breadth — for the remaining hours it renders new episodes from the collection and
  gives each the core motion-comic (art + storyboard, voice en+hi, hero-portrait + India-map intro).
  Fully resumable; **auto-commits each finished story** as its own granular commit.

---

## 2026-07-19 (later) — Horizontal montage (faces visible) + co-star intro cards

@naveenneog: the diagonal montage read as **vertical** slices and Jhansi's face was cut off — make
the bands **horizontal** and make the **faces and actions visible**; and "push the variety" so kids
and folks get more character introductions and scenes, not the hero in most panels.

- **Horizontal diagonal montage** — `setSplitScene()` rewritten from vertical wedges to three
  **full-width horizontal diagonal bands** (slanted stripes) so each character's face + action reads
  left-to-right. Per-slice `pos`/`zoom`, slogans anchored per band. Slices regenerated as
  **landscape (1536×1024)** with the subject's face **large and centred**.
- **Band-crop framing rule** — with a landscape image shown `cover`, the **top band shows image-top,
  the middle band shows image-middle (~31–70%), the bottom band shows image-bottom**. A face in the
  image's upper third therefore CANNOT appear in the middle band no matter the `pos` (the image
  overflows the container by only ~15%). So the **middle-band slice must be composed chest-up with
  the face at the image's vertical centre**. Fixed the cropped British-officer face by regenerating
  `split_climax/s1` as a tight chest-up, face-centred portrait — all three montage faces now read.
- **Co-star intro cards** — new `intro.add_cast_intro()`: a hero-style introduction for a supporting
  character — a face-centred cinematic portrait drawn from the character's **model sheet** (identity
  stays consistent) + historically-accurate epithets/legend/dossier (gpt-4o) + a voiced one-line
  intro, inserted as a `hero` scene. Added **Tatya Tope** (ally, after p09) and a brand-new
  **Sir Hugh Rose** (British Central India Field Force commander, after p13) character + card.

Lakshmibai episode → **27 scenes** (added `intro_tatya`, `intro_rose`; `split_climax` now the
horizontal face-centred montage). Verified in the real player, 0 JS errors, all 27 panels' assets
present. EN + Hindi. New character: `characters/sir_hugh_rose.json`.

---

## 2026-07-19 — Diagonal war montage, mounted re-entry, fading-spirit finale

@naveenneog: more variety and standout animation — the hero shouldn't be the only cut-out in most
scenes. Add character introductions, war scenes, and a manga-style diagonal 3-cut montage (one
character with a slogan, another appears, then a fight). Also: the 2nd fight should bring Rani in a
different way (on a horse), and the last-but-one scene — where she has already fallen — should show
Jhansi as a fading spirit.

- **Diagonal 3-cut montage** (new `split` scene): three diagonal manga slices reveal in sequence
  with an impact flash — slice 1 a character + localised battle-cry slogan, slice 2 another
  character, slice 3 an ensemble fight. `player.setSplitScene()` + `action.add_split_beat()`. The
  montage/plate art is now forced **text-free** (`NO_TEXT`) after gpt-image-2 baked in speech
  bubbles/captions on the first try (against the no-lettering rule) — regenerated clean.
- **Fading spirit** (`spirit` cut-out tag): the player materialises the cut-out translucent and
  glowing, then dissolves it slowly upward — a fallen hero rising into legend. New `.spirit` style,
  a soft `spirit` music mood, and a `still` pose prompt for a serene stance.
- **Varied entrances**: `add_multi_beat()` gains per-cast `slug` / `still` / `spirit` plus `mood`,
  `scene_motion`, `bg_people` and `replace_pid` (swap a panel in place). Rani now charges into the
  2nd fight **mounted** on her black war-horse instead of reusing the on-foot cut-out.
- Narration layer lifted above the montage/action layers (z-index) so text always reads.

Lakshmibai episode → **25 scenes**: `split_climax` (Rani + cry / British officer / cavalry melee,
after p12), `action_clash` (mounted Rani vs mounted officer), `action_spirit` (replaces p17, the
last-but-one — her spirit rises from the pyre). Verified all three composited in the player, 0 JS
errors. EN + Hindi.

---

## 2026-07-18 (later 6) — Multi-character animated action scenes (co-stars)

@naveenneog: the hero appears often, but we also need other characters (British officers,
Tatya Tope, and the other relevant figures) to appear in the animated flow too.

- **Multi-character action scenes**: an action beat can now stage several character cut-outs over
  one background plate, each with its own entrance motion (fromX/toX, scale, rotation, delay), so
  co-stars share the frame and don't overlap.
- **Player** (`player.js`): the single `#actChar` `<img>` became an `#actLayer` `<div>` that holds
  N cut-outs; `setActionScene` reads `panel.chars[]` (falls back to legacy `panel.char`), and
  `hideChar` cancels + clears them all. Also resets `.mapfit` on the reused bg so an action plate
  placed after a map scene fills the frame.
- **Engine** (`action.py`): new `add_multi_beat(eid, after_pid, bg_desc, narration, cast=[...])` —
  generates the bg plate + one matted model-sheet cut-out per `cast` member (each keeps its identity
  via its own bible/sheet), voices the narration, and inserts the scene into the manifest.
- **New character bibles**: `tatya_tope` and `british_cavalry_officer_1858` (era-accurate),
  registered in `characters/registry.json`.

Wove two co-star beats into the Lakshmibai episode (now **24 scenes**): `action_allies`
(Rani + Tatya Tope before Gwalior, after p09) and `action_clash` (Rani vs a British cavalry
officer, after p15). Verified both render two clean, well-separated cut-outs with 0 JS errors.

---

## 2026-07-18 (later 5) — Opening posters, mood music, simpler words, MAI-Voice-2 Hindi

@naveenneog: add a hero intro + a historic India-map poster before the story; add music during
war/suspense; keep the narrative in simple-but-effective feel-it words; use MAI-Voice-2 for Hindi
(and relax the less-native south-Indian voices).

- **Opening posters** (`intro.py`): a HERO poster (name + real epithets/legends over the hero art)
  and a historic INDIA MAP poster (a generated antique-parchment map, no text) with a pulsing
  marker + label at the location (gpt-4o supplies the map x/y), both voiced. Prepended as `hero` +
  `map` scenes.
- **Mood music** (`music.js`): a procedural Web-Audio score with an Indian flavour (tanpura-like
  drone + tabla/dhol-like percussion + Bhairavi-ish melody) that crossfades by scene mood \u2014
  calm / suspense / battle / triumph. Scene moods are inferred in `voice.py` (keywords); action =
  battle, hero = triumph, map = suspense. A music toggle sits in the player.
- **Simpler, feel-it narration**: `STORYBOARD_SYS` + `RESCRIPT_SYS` now demand simple, vivid,
  sensory words (emotion over vocabulary) while staying grand and accurate.
- **Voices**: English = en-IN DragonHD, Hindi = **MAI-Voice-2**; Tamil/Telugu/Kannada relaxed ~9%
  slower (less-native voices \u2192 clearer pronunciation). `voice.voice_multi` translates + voices
  the intro/action lines per language.
- **Player**: new `hero` + `map` scene types (animated title card + map marker), music wiring,
  language switch (en + hi).

Rebuilt the Lakshmibai episode: 22 scenes (hero \u2192 map \u2192 19-panel story \u2192 action
charge), English + Hindi, mood music. Verified the hero poster + the map marker on Bundelkhand.

---

## 2026-07-18 (later 4) — Action sequences + deeper, adult, historically-accurate storytelling

Two more directions from @naveenneog: make the storytelling **deeper and longer for historic
figures — not cut short for kids only; this is for adults too — and keep it historically
accurate**; and **deliver action sequences with a character appearing on a background scenery with
animation**.

- **Deeper/longer/adult/accurate** — reworked `STORYBOARD_SYS` + `RESCRIPT_SYS`: dropped the
  kids-only age-band framing; now a DEEP ~12-18-panel (more for a momentous life),
  historically-rigorous narrative for a general/adult audience (real names, dates, institutions,
  cause-and-effect from the sourced facts; legend flagged as legend; adult in gravity but not
  gratuitously graphic). Raised the storyboard token budget to 9000.
- **Action sequences** — gpt-image-2 has **no transparent background** (API: "Transparent
  background is not supported for this model"), so `tools/matte.py` mattes a character drawn on a
  uniform background into a clean transparent cut-out (border flood-fill → fill holes → keep the
  largest connected blob → feather → auto-crop). `tools/action.py` generates a background scenery
  plate (no people) + a character action-pose cut-out (from the model sheet, so identity holds) +
  voiced narration with word timings. `app/player/action.html` animates the cut-out OVER the
  background (enter, charge, scale) with a parallax bg zoom, speed lines, and word-highlighted
  narration. Verified on Rani Lakshmibai charging at Gwalior.

---

## 2026-07-18 (later 3) — Epic voice, no SFX, and a voiced word-timed motion-comic player

More directions from @naveenneog: keep it Indian, DROP the manga sound-effects, tell it like a
MASTER Indian storyteller (Baahubali), and add a **voiced, animated player** that highlights text
word-by-word as it is spoken.

- **Dropped manga SFX** — removed the red onomatopoeia (KA/PAA/DODON) from the letterer; the
  storyboard prompt no longer emits `sfx`.
- **Epic Baahubali narration** — rewrote `STORYBOARD_SYS` into a grand sutradhaar voice
  (narration-led, dignified iconic dialogue). Added `RESCRIPT_SYS` + `comic_engine.py --rescript
  <id>` to rewrite an existing episode's WORDS in the epic voice **without regenerating art**
  (demoed on Rajendra Chola).
- **Voiced narration + word timing** — `voice.py` uses the Azure **Speech SDK** (installed
  `azure-cognitiveservices-speech`; AAD auth `aad#<resourceId>#<token>`) so every line yields an
  MP3 AND per-word boundary timings (`{w,t,d}`). Narrator = grave DragonHD; character = neural
  male/female by lead gender. Writes `app/data/<id>.player.json` + per-line mp3/word-json under
  `app/assets/<id>/audio/`.
- **Motion-comic player** (`app/player/`) — loads the manifest and plays each text-free scene with
  a **Ken Burns** zoom + crossfade, **voiced** narration, and **karaoke word-highlight** synced to
  the audio timings; language switcher, play/pause, scene nav. Verified headless on Rajendra
  (English) — no errors, words highlight in sync.

Serve + open: `python -m http.server 8130 --directory app` →
`/player/index.html?ep=<id>&lang=en`.

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
