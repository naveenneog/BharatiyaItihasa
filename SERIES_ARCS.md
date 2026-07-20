# Multi-Episode Story Arcs — Bhāratīya Itihāsa

Major figures and dynasties get **arcs of several episodes** — their glory, craftsmanship, the lands
they conquered, and how they ruled — **not one-offs**. Good news: `indian_history_collection.json`
is **already structured as arcs** (85 episodes across three eras). The job is to *build* them and to
keep the three era-timelines growing in parallel.

Status: **✅ built** · **⏳ queued** (in the corpus, will auto-build) · **📝 idea** (add later).
Every episode is built to the same bar: character-consistent anime art, hero + India-map intro,
face-forward hero portrait, an **animated action beat + 3-band montage (clear faces & action)**,
voiced & word-highlighted in English + हिंदी, historically accurate and adult-length. Recurring
figures (e.g. Rajendra across two Chola episodes) reuse their character bible, so the same face
carries across an arc.

---

## 🏛️ The Chola Age  *(Medieval — the example that sparked this)*  — **build priority #1**
Glory, craftsmanship, the seas they sailed and the land they ruled:
1. **Rajaraja Raises Brihadisvara** — ⏳ — the emperor raises the towering Thanjavur temple; granite,
   gods and the craftsmanship of a golden age. *(glory + craft)*
2. **Rajendra Brings the Ganges South** — ✅ — the northern expedition to the Ganga; the new capital
   Gangaikonda Cholapuram. *(conquest)*
3. **Tamil Merchant Guilds Sail the Indian Ocean** — ⏳ — the Ainnurruvar/Manigramam guilds and the
   Chola thalassocracy across Southeast Asia. *(the seas they ruled)*
4. **Chola Bronze Artists Make the Divine Dance** — ⏳ — the lost-wax Nataraja bronzes; sacred art at
   its peak. *(craftsmanship)*
5. **The Chola Village Chooses Its Guardians** — ⏳ — the Uttiramerur inscriptions and village
   self-government; how the Cholas actually *ruled*. *(rule)*

## ☸️ Maurya & 🌸 Gupta — the Classical Age  *(Ancient)*
- **Chandragupta and Chanakya Build an Empire** ⏳ · **Ashoka's Kalinga Change of Heart** ✅ ·
  **Samudragupta's Pillar of Many Realms** ⏳ · **Vikramaditya and the Iron Pillar's Riddle** ⏳ ·
  **Aryabhata and Brahmagupta Measure the Sky** ⏳ *(science & the golden age)*.

## ⚔️ Rajput Valour  *(Medieval)*
- **Prithviraj at Tarain** ⏳ · **Maharana Pratap Keeps the Hills Free** ⏳ ·
  **Rana Kumbha Raises Kumbhalgarh** ⏳ · **Warangal's Stone Gateways (Kakatiya)** ⏳.

## 🚩 Maratha Swaraj  *(Medieval → early modern)*
- **Shivaji's Quiet Escape from Agra** ✅ · **Bajirao's Swift Ride to Delhi** ⏳.
  📝 ideas: *Tanaji at Sinhagad*, *Coronation at Raigad*.

## 🏰 Vijayanagara & 🌊 Frontier Guardians  *(Medieval — incl. Unsung Heroes)*
- **Krishnadevaraya and the Raichur Resolve** ⏳ · **Hampi Amazes the Travellers** ⏳.
- **Lachit Barphukan Holds the Brahmaputra** ⏳ · **Sukaphaa Begins the Ahom Story** ⏳ ·
  (📝 *Rani Abbakka vs the Portuguese*, *Kanhoji Angre*).

## 🔥 The Great Revolt of 1857  *(Freedom Struggle — a built multi-hero mosaic)*
Rani Lakshmibai ✅ · Tatya Tope ✅ · Kunwar Singh ✅ · Bahadur Shah Zafar ✅ · Mangal Pandey ✅.
📝 ideas: *Begum Hazrat Mahal*, *Nana Sahib at Kanpur*.

## 🕊️ The Long Freedom Struggle  *(Freedom Struggle — beyond 1857)*
Bagha Jatin ✅ · Tilak ✅ · Lala Lajpat Rai ✅ · Khudiram Bose ✅.
📝 ideas: *Bhagat Singh*, *Chandrashekhar Azad*, *Subhas Bose & the INA*, *Sarojini Naidu*.

---

### Build strategy
`grow.py` breadth now (a) builds the **Chola arc first**, then (b) **round-robins the three series**
(Freedom Fighters · Unsung Heroes · Ancient & Medieval) so **all three era-timelines grow together**
— the home page fills out across eras instead of finishing one era before starting the next. To add a
brand-new arc, append its episodes (schema: `order, title, figure, era, region, age, logline, moral,
sources[]`) to the right book in `indian_history_collection.json`; unbuilt episodes are picked up
automatically.
