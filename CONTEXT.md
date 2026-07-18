# CONTEXT — "Bhāratīya Itihāsa" / Indian History app · RESUME ANCHOR

> **Read this file first** to resume the Indian History app in a fresh session **without
> touching the Indian Tales session/pipeline**. It captures the vision, current status, the
> full reusable **Storyteller** pipeline, the exact operational workflow, and the decisions
> still open. Sibling app to **Indian Tales** (live: https://api-naveen.web.app), but this one
> deploys to its **own separate endpoint**.

---

## 0. RESUME HERE (start of any new session)

**What exists now (2026-07-18):**
- `ROADMAP.md` — vision, pillars, authentic-sourcing standard, candidate figures, phases, open decisions.
- `indian_history_collection.json` — **Phase 0 corpus, first pass = 50 cited episodes** across 3 pillars
  (Freedom Fighters 17, Unsung Heroes 14, Ancient→Medieval 19). Schema mirrors the Indian Tales
  collection so it flows through the same pipeline.
- `research/` — the raw per-pillar research fragments (with citations + fact-vs-tradition notes):
  `freedom_fighters.json`, `unsung_heroes.json`, `ancient_medieval.json`
  (+ **batch-2 expansion** fragments `figures_batch2.json`, `ancient_medieval_batch2.json`, and a
  `expansion_themes.md` briefing — added when the expansion research finishes).
- The **Storyteller skill** (reusable engine): `C:\Users\navg\DailyApps\dailyapps-skills\storyteller\`.

**Nothing is generated/built/deployed yet** for Indian History — Phase 0 is research only.

**To move forward, resolve the 4 OPEN DECISIONS (see §7), then do Phase 1 (pilot):**
1. Merge all research fragments → final `indian_history_collection.json` (see §4 build_queue mapping).
2. Scaffold the app from the Storyteller skill `template/` onto a **new endpoint** (§5).
3. Generate a 12-episode pilot with the autonomous harness (§3), finalize + deploy, verify.
4. Then Phase 2 = full build-out via the same monitored batch harness.

**Do NOT disturb the Indian Tales session** — that pipeline/monitoring runs independently in another
session. This app has its OWN repo, OWN Firebase site, OWN autogen_status/ledger.

---

## 1. Vision (short)

Retell India's **actual, record-based** history — ancient → medieval → freedom struggle — as short,
dignified, illustrated, narrated, 6-language episodes celebrating the glory, valour and ingenuity of
Indians (kings, queens, empires, scholars) and especially **unsung heroes**. Every episode's key
claims trace to **primary/scholarly records** (epigraphy, chronicles, archives), NOT Wikipedia
paraphrase. Celebratory but truthful; neutral & unifying; adversaries with dignity; no communal framing.

## 2. Pillars → app sections (proposed; confirm in §7)

- **Freedom Fighters** — independence struggle (1857–1947)
- **Unsung Heroes** — under-celebrated figures across all eras (explicit focus)
- **Ancient India**, **Classical & Southern Powers**, **Medieval Valour**, **Empire/Science & Culture**
  — (the Ancient→Medieval pillar; may split into these sub-sections or stay as 1-2 sections)

Section taxonomy is a decision. The pipeline groups episodes by a `section`/`series` string and the app
derives per-section counts, so taxonomy is easy to change later.

---

## 3. THE STORYTELLER PIPELINE (reused engine — the core know-how)

The Indian Tales app is built by a proven pipeline. **Reuse it verbatim** for Indian History; only the
*content collection*, *style bible*, and *endpoint* change. Canonical implementation lives in
`C:\Users\navg\DailyApps\IndianTales\tools\` and is mirrored in the **Storyteller skill**.

### 3.1 Per-tale flow
`spec (storyboard JSON) → build_tale.py → app/assets/<id>/{img,audio/<lang>}, app/data/<id>.json`
- **Illustrations:** Azure **gpt-image-2** (moderation-aware: handles 400/401/429 gracefully; a
  fully-blocked tale ends up blank and must be excluded at publish — see §3.5).
- **Narration:** Azure Speech neural TTS, **6 languages** en/kn/hi/ta/te/de, multi-voice
  (narrator + male/female character voices + a unison moral), stitched with ffmpeg.
- **Translation:** Azure OpenAI gpt-4o (`Panchatantra/tooling/loc_translate.py`, shared).

### 3.2 Autonomous batch generation (`autogen.py`) — the workhorse
- `build_queue()` merges a priority `STORY_PLAN.json` then the rest of the `collection` JSON, filtered
  to kid-safe **age A/B/C**, deduped vs already-built, round-robined across sections.
- `make_spec(item)` auto-authors a full storyboard spec via **gpt-4o** from the episode's
  (title, age, logline, moral) + a **style bible** (for Tales = Togalu-Gombe shadow-puppets; for
  **History pick a style — see §5**), then `build_tale.process_spec` renders it.
- **Hardened & resumable:** 45-min per-tale wall-clock budget (`TALE_BUDGET_S`, daemon worker thread —
  a hung tale self-abandons and the loop continues; abandoned threads often still finish in the
  background = "bonus" tales), catches `SystemExit`, az-token retry 3×/120s, writes `autogen_status.json`
  after every tale, self-finishes at a `--hours` deadline OR when the queue drains (writes `finished`).
- Run: `cd tools; $env:PYTHONIOENCODING="utf-8"; python autogen.py --hours <N>`

### 3.3 The anti-throttle "keepactive" guard (CRITICAL on this machine)
This Windows box **throttles background compute ~4× when idle** (Modern Standby); a ~30-min tale
balloons to 100+ min. `SetThreadExecutionState` and `standby-timeout=0` do NOT help. The fix that DOES:
a detached PowerShell loop firing a **synthetic zero-delta mouse event** every 25s. **Start it BEFORE
every run and leave it running until finalize.**
```powershell
$sig='[DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags,uint dx,uint dy,uint dwData,System.IntPtr dwExtraInfo);'
$m=Add-Type -MemberDefinition $sig -Name KA -Namespace W -PassThru
while($true){$m::mouse_event(0x0001,0,0,0,[IntPtr]::Zero);Start-Sleep 25}
```
(Note: a Microsoft-Store Python shows **two** python.exe for **one** run — that's normal.)

### 3.4 The monitoring-schedule pattern (unattended runs)
For long/overnight runs, create a **recurring 30-min scheduled prompt** that each tick: reads
`autogen_status.json`; confirms the autogen + keepactive processes are alive; relaunches autogen if it
died or the newest asset is >50 min stale (and before deadline); relaunches keepactive if it died; and
when the run has `finished` (or is past deadline / no autogen running) performs the **finalize** (§3.5)
then **stops itself**. Keep check-ins to 2-3 sentences. (This session used schedules #14–#17 this way.)

### 3.5 Finalize workflow (watermark → publish → QA → commit → deploy)
1. Stop `storygen` + `keepactive`; kill any lingering autogen python by PID.
2. **Precise partial:** if `status.current` names a tale with NO `app/data/<id>.json`, move its
   `app/assets/<id>` aside to `_incomplete_hold` (budget-"failed" tales that DID finish in the
   background — data.json + ~7-8 imgs + ~48-54 audio — are KEPT; publish picks them up).
3. `python watermark.py` — idempotent logo stamp (regenerates from `img_raw/` originals).
4. `python publish.py` — builds the CDN `publish/v1/` spine (AVIF/WebP re-encode, split schema,
   `catalog.json` with auto-incremented version). ~1 min/tale at full speed; writes catalog LAST.
5. **QA needs a local server** (qa_it.py hits http://127.0.0.1:8124): `& deploy\build_dist.ps1` to
   assemble `dist/`, then serve it detached `cd dist; python -m http.server 8124`, confirm
   `/v1/catalog.json` → 200, then `python qa_it.py` (expect `console: []`, correct sections, section
   counts summing to total, `langbar_chips: 6`). Stop the server after.
6. **Exclude blank-image tales:** for any catalog tale with `bytes.img == 0`, remove it from the
   catalog `tales` array, delete `publish/v1/{audio,img,tales}/<id>`, move `app/data/<id>.json` +
   `app/assets/<id>` to `_incomplete_hold`, re-run qa.
7. **Commit masters first** (nested repo under `app/assets`, own remote), **then** the main-repo spine
   (`publish/v1 app/assets tools app/data app/app.js app/sw.js autogen_ledger.json autogen_status.json`).
   Use `git -c user.name="naveenneog" -c user.email="naveen4api@gmail.com"` + a
   `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer.
8. **Deploy:** `& deploy\deploy_gcp.ps1` (build_dist + `firebase deploy`), then verify live catalog
   `version`+count (cache-bust `?cb=<random>`), that new episodes resolve HTTP 200, and pending == 0.

### 3.6 Adding a NEW section end-to-end (4-file wiring pattern)
Learned building the Tenali Rama section. To add a section/series:
1. **Collection JSON** — append a `series` object with `books[].episodes[]` (each: `order, title, age,
   logline, moral`; History also carries `figure, era, region, sources[], notes`).
2. **`tools/autogen.py`** — add the series to `SERIES_META` (author, origin, subtitle) and to the
   round-robin `order` list in `build_queue()`. (`SERIES_DISPLAY` only if the display name differs.)
3. **`tools/publish.py`** — add the section to `SECTION_ORDER` (controls app ordering).
4. **`app/app.js`** — add `SECTION_ICON[<name>]` (an emoji) and a 6-language `SECTION_L10N[<name>]`
   entry (accordion header label), then bump the `CACHE` version in `app/sw.js`.
Verify: `python -c "import autogen; ..."` shows the new episodes in `build_queue()` as pending.

---

## 4. Content collection format & build_queue mapping

`build_queue()` reads `series[].books[].episodes[]` and keeps episodes with `age in (A,B,C)`
(A=3-5, B=6-8, C=9-12), skipping ones matching the block/dup regexes (avoid gore words in loglines).
Each episode needs at minimum: `title`, `age`, `logline`, `moral`. History episodes additionally carry
`figure, era, region, sources[] ({type,citation,note}), notes` — the extra fields are harmless to the
tale pipeline and available to show a "Sources" line in the reader.

**Merging the research fragments:** all `research/*.json` fragments use the same shape. Merge them into a
single `indian_history_collection.json` with one `series` per pillar (Freedom Fighters, Unsung Heroes,
Ancient & Medieval India — or your chosen taxonomy), de-duplicating figures that appear in >1 pillar
(this session kept overlaps in Freedom Fighters, dropped them from Unsung Heroes), then re-sequence each
series' `order` 1..N and refresh top-level `series_count`/`episode_count`.

---

## 5. Standing up the NEW app on a SEPARATE endpoint

- **New repos:** one app/spine repo (e.g. `github.com/naveenneog/indian-history`) + one **masters**
  repo for the raw PNG/MP3 (like `indian-tales-masters`, kept as a nested git repo under `app/assets`).
- **New Firebase Hosting site** (separate from `api-naveen`): either a new Firebase project, or a second
  Hosting **site** on the same project — `firebase hosting:sites:create indian-history` →
  `https://indian-history.web.app`, with its own `firebase.json`/`.firebaserc` target. Same-origin `/v1`
  spine, same headers as Indian Tales (`firebase.json`: `public: dist`, CORS on `/v1/**`, no-cache on
  catalog/sw/index, immutable on img/audio).
- **Scaffold:** copy the Storyteller skill `template/` → `app/`, set brand/title/icon, empty
  `v1/catalog.json`. Point `autogen.py`'s `COLLECTION` path at `indian_history_collection.json` and set
  a **history style bible** in `make_spec` (DECISION §7: period-accurate "illustrated heritage" —
  Ajanta-mural / Indian-miniature / Company-school look, era-accurate costume/architecture — vs. keeping
  the Togalu-Gombe shadow-puppet style for brand continuity). Consider a graver "chronicler" narrator.
- **Independent** `autogen_status.json` / `autogen_ledger.json` / catalog versioning.

---

## 6. Voice config (carry over; tweak for gravitas)

- **English** = en-IN **DragonHD**, narrator varied per tale (5 female DragonHD rotated for
  female-narrated tales; the single male en-IN DragonHD **Arjun** for male-narrated; male dialogue =
  en-IN-Prabhat neural).
- **Hindi** = native **MAI-Voice-2** mix (hi-IN Arjun/Dhruv/Kavya/Priya rotated).
- **kn/ta/te/de** = existing neural voices.
- **Azure access:** resource `ai-contosohub530569751908` (region eastus2). TTS endpoint
  `https://{region}.tts.speech.microsoft.com/cognitiveservices/v1`, header
  `Authorization: aad#{RESOURCE_ID}#{AAD-token}` (NO "Bearer" prefix). Token via
  `az account get-access-token --resource https://cognitiveservices.azure.com`. SSML pitch must be
  `"0%"` (not `"0st"` → HTTP 400). gpt-image-2 + gpt-4o via the same cognitiveservices endpoint.

## 7. OPEN DECISIONS (resolve before Phase 1)

1. **App name + endpoint** — e.g. `indian-history.web.app` / `bharat-itihasa` / `itihasa-naveen`.
2. **Art direction** — period-accurate illustrated heritage **vs.** shadow-puppet continuity.
3. **Section taxonomy** — the pillar→section mapping in §2.
4. **Phase-0 corpus target size** — how many episodes for the pilot and full build.

## 8. Prerequisites (a fresh machine/session)

- `az login` (AAD only; keys disabled) with access to the cognitiveservices resource above.
- `ffmpeg` on PATH. Python 3 with `playwright` (`pip install playwright; python -m playwright install
  chromium`) for QA. `firebase-tools` (`npm i -g firebase-tools`; `firebase login`).
- Windows: use the **keepactive** guard for every batch run (§3.3).
- Prefer the **Storyteller skill** for the engine; this CONTEXT for the History-specific plan.

## 9. Pointers

- Roadmap: `IndianHistory/ROADMAP.md` · Corpus: `IndianHistory/indian_history_collection.json` ·
  Research: `IndianHistory/research/*` · Engine: `dailyapps-skills/storyteller/` (and canonical
  `IndianTales/tools/`). Live sibling app for reference UX: https://api-naveen.web.app
