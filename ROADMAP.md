# Roadmap — "Bhāratīya Itihāsa" (Indian History) · Historic Figures & True History

> Sibling app to **Indian Tales** (https://api-naveen.web.app). Same PWA presentation
> (illustrated, narrated, 6-language, hero carousel + reader), **separate content spine
> and separate deployment endpoint.** This is a roadmap, not yet a build.

---

## 1. Vision

Retell **India's actual history** — ancient → medieval → the freedom struggle — as short,
dignified, illustrated episodes that celebrate the glory, power, valour and ingenuity of
Indians: kings and queens, empires, scholars, and above all the **unsung heroes** history
forgot. Every episode is grounded in **authentic records** (epigraphy, primary chronicles,
archaeology, archives) — **not Wikipedia paraphrase.** Wikipedia may only be an index to
find the primary source; the episode is written from the record itself, with citations.

Tone: celebratory but **truthful and evidence-based**. Valour without distortion; contested
history handled with sources and neutrality; no communal framing; human dignity throughout.

---

## 2. Content pillars & sections

Presented under one app, two pillars, grouped into sections (mirrors the Indian Tales
`sections` model — a `section` field per episode; app derives counts):

**Pillar A — Historic Figures** (biographical arcs)
- `Freedom Fighters` — the independence struggle (1857 → 1947)
- `Unsung Heroes` — under-celebrated figures across all eras (explicit focus)

**Pillar B — Indian History (ancient → medieval)** (events, reigns, turning points)
- `Ancient India` — Mauryas, Guptas, Kalinga, Satavahanas, Sangam age
- `Classical & Southern Powers` — Cholas, Chalukyas, Pallavas, Rashtrakutas, Vijayanagara
- `Medieval Valour` — Rajputs, Marathas, Ahoms, regional resistances
- `Empire, Science & Culture` — Nalanda/Takshashila, mathematics/astronomy, maritime trade,
  administration & law (e.g., Chola local self-governance)

> Naming/section list is a **decision point** — confirm with user before Phase 1.

---

## 3. Sourcing standard (the core differentiator)

**Every episode must trace its key claims to at least one primary or scholarly source, stored
as a `sources[]` list in the episode record (with a short citation line shown in the reader).**

Source hierarchy (prefer top-down):
1. **Epigraphy / inscriptions** — Ashokan edicts; Hathigumpha (Khāravela); Allahabad Pillar
   praśasti (Samudragupta, by Harishena); Aihole inscription (Pulakeśin II, by Ravikīrti);
   Uttaramerur & Thanjavur inscriptions (Chola governance); Gwalior/Junagadh inscriptions.
2. **Primary chronicles & texts** — Kauṭilya's *Arthaśāstra*; Megasthenes' *Indica* (via
   Arrian/Strabo); Xuanzang & Faxian travel records; Al-Bīrūnī's *Kitāb-ul-Hind*; Kalhaṇa's
   *Rājataraṅgiṇī*; *Bāburnāma*; Abul Fazl's *Āin-i-Akbarī*; Sabhāsad *Bakhar* & Jedhe
   *Shakāvalī* (Shivaji); Ibn Battuta's *Riḥla*; Ferishta.
3. **Archaeology / numismatics / ASI** — site reports, Gupta & Chola coinage, monuments.
4. **Archives & freedom-struggle records** — National Archives of India; INA records; court
   statements & writings (Bhagat Singh's jail notebook & statements; Bose's speeches/letters);
   contemporary newspapers; gazetteers.
5. **Scholarly secondary (for synthesis, never the sole basis)** — R.C. Majumdar (*History &
   Culture of the Indian People*), Nīlakaṇṭa Śāstri (*A History of South India*), Romila
   Thapar, Jadunath Sarkar (Shivaji/Aurangzeb), Satish Chandra, D.C. Sircar (epigraphy).

**Fact-check pass:** a dedicated citation/accuracy step before an episode is published; flag
legendary/bardic material (e.g., *Pṛthvīrāj Rāso*) as tradition, not fact.

---

## 4. Candidate figures & episodes (research seed — not final)

**Ancient:** Chandragupta Maurya & Chāṇakya · Ashoka (edicts, Kalinga) · Khāravela of Kalinga ·
Samudragupta · Chandragupta II Vikramāditya · Gautamīputra Sātakarṇi · Porus (Puru).

**Classical / South:** Rājarāja Chola I & Rājendra Chola I (Gangaikonda, SE-Asia campaigns) ·
Pulakeśin II (defeat of Harsha) · Narasimhavarman Pallava · Krishnadevarāya (Vijayanagara).

**Medieval valour:** Pṛthvīrāj Chauhān · Rāṇā Kumbha · Mahārāṇā Pratāp (Haldighati) ·
Chhatrapati Shivaji Mahārāj · Lachit Barphukan (Saraighat) · Rani Durgāvatī · Suheldev.

**Freedom struggle:** Rani Lakshmibai · Mangal Pandey · Kunwar Singh · Tatya Tope ·
Bal Gangadhar Tilak · Bhagat Singh · Chandrashekhar Azad · Subhas Chandra Bose · Sardar Patel ·
Begum Hazrat Mahal · Birsa Munda · Alluri Sitarama Raju.

**Unsung heroes (explicit pillar):** Uda Devi · Jhalkari Bai · Velu Nachiyar & Kuyili ·
Kittur Chennamma · Rani Gaidinliu · Matangini Hazra · Kanaklata Barua · Tirot Sing ·
Tilka Manjhi · Ashfaqulla Khan · Rajguru · Pingali Venkayya · Peer Ali Khan · Potti Sreeramulu ·
Tanguturi Prakasam · Parbati Giri.

---

## 5. Presentation & pipeline reuse

- **Same PWA UX** as Indian Tales: 6 languages (en/kn/hi/ta/te/de), hero carousel, accordion
  sections, offline reader, watermark, `/v1` content spine.
- **Art direction (DECIDED 2026-07-18):** **shonen-manga / action-anime graphic novel**
  ("Naruto-style" dynamic action + comic dialogue), with **character consistency** — each figure
  gets a canonical model sheet reused across panels via gpt-image-2 `images/edits`. Historical
  integrity kept *within* the anime idiom (era-accurate costume/weapons/architecture from
  `sources[]`; valour without gore). See `CHANGELOG.md` for the mechanism + verification.
- **Reuse the toolchain** (`autogen.py` → `build_tale.py` → `watermark.py` → `publish.py` →
  `qa_it.py` → `deploy_gcp.ps1`) with three swaps: (1) a new **history collection** JSON +
  `STORY_PLAN.json`, (2) a new **style bible** (era-accurate), (3) a new **endpoint config**.
- **Voices:** same en-IN DragonHD + native MAI-Voice-2 Hindi mix; consider a graver
  "chronicler/narrator" register for history.

---

## 6. Separate deployment (different endpoint)

- **New repo** (e.g., `github.com/naveenneog/indian-history`) + **new masters repo**.
- **New Firebase Hosting site/target** — either a new Firebase project or a second Hosting
  **site** on the same project (`firebase hosting:sites:create indian-history` →
  `indian-history.web.app`), served same-origin with its own `/v1` spine. **Confirm endpoint
  name** (candidates: `bharat-itihasa`, `indian-history`, `itihasa-naveen`).
- Independent catalog versioning; independent autogen ledger/status.

---

## 7. Phases

- **Phase 0 — Research corpus (the heavy lift).** Build `indian_history_collection.json`:
  per figure/event → logline, the historical arc (Invocation→Rise→Struggle→Legacy), the moral/
  takeaway, **and `sources[]` with real citations.** This is where the "actual records"
  standard is enforced. ~100–150 episodes target.
- **Phase 1 — Pilot (12 marquee figures)** spanning all eras (e.g., Ashoka, Rājendra Chola,
  Maharana Pratap, Shivaji, Lachit, Rani Lakshmibai, Bhagat Singh, Bose, Birsa Munda,
  Chāṇakya, Krishnadevarāya, an unsung hero). Validate art style + accuracy pass + endpoint.
- **Phase 2 — Build-out** of the full corpus via the autogen batch pipeline (with the same
  keep-active + budget + monitoring-schedule harness proven on Indian Tales).
- **Phase 3 — Depth & regional balance** — unsung heroes, regional/tribal resistances,
  science/culture episodes; ensure geographic & chronological balance.

---

## 8. Guardrails

- **Historical integrity first** — evidence over legend; label tradition as tradition.
- **Neutral & unifying** — celebrate valour and achievement without communal/derogatory framing;
  present adversaries with basic dignity; stick to what records support.
- **Age-appropriate** — battle/valour told without gratuitous gore (reuse the moderation-aware
  image handling).
- **Citations visible** — a short "Sources" line per episode builds trust and teaches.

---

## 9. Open decisions for the user (before Phase 1)

1. App/brand name + **endpoint** (`indian-history.web.app`? `bharat-itihasa`?).
2. **Art direction — DECIDED (2026-07-18): shonen-manga / action-anime graphic novel** with
   **character consistency** (Naruto-style action + comic dialogue). See `CHANGELOG.md`.
3. Section taxonomy (the list in §2) — approve or adjust.
4. Scope of Phase 0 corpus (target episode count) and any must-include figures.
