#!/usr/bin/env python3
"""Generate per-line neural TTS WITH word timings + a motion-comic player manifest.

Uses the Azure Speech SDK (AAD auth) so each line yields an MP3 AND word-boundary timings
(start/duration per word) for karaoke-style highlighting. Reads the saved storyboard (panels +
dialogue + i18n), synthesises one clip per line per language, and writes
`app/data/<id>.player.json` for the motion-comic player.

  cd tools; $env:PYTHONIOENCODING="utf-8"
  python voice.py ashoka_s_kalinga_change_of_heart --langs en      # quick (one language)
  python voice.py ashoka_s_kalinga_change_of_heart                 # all 6 languages
"""
import argparse, html, re, subprocess, sys, time
import azure.cognitiveservices.speech as speechsdk
import common as C

sys.stdout.reconfigure(encoding="utf-8")

REGION = "eastus2"
RID = ("/subscriptions/e839ff0f-532b-4828-a2b3-8c9a1b719d85/resourceGroups/rg-contosohub/"
       "providers/Microsoft.CognitiveServices/accounts/ai-contosohub530569751908")
CS_SCOPE = "https://cognitiveservices.azure.com"

NARR = {"en": "en-IN-Arjun:DragonHDLatestNeural", "kn": "kn-IN-GaganNeural",
        "hi": "hi-IN-Dhruv:MAI-Voice-2", "ta": "ta-IN-ValluvarNeural",
        "te": "te-IN-MohanNeural", "de": "de-DE-ConradNeural"}
MALE = {"en": "en-IN-PrabhatNeural", "kn": "kn-IN-GaganNeural", "hi": "hi-IN-Arjun:MAI-Voice-2",
        "ta": "ta-IN-ValluvarNeural", "te": "te-IN-MohanNeural", "de": "de-DE-KillianNeural"}
FEMALE = {"en": "en-IN-NeerjaNeural", "kn": "kn-IN-SapnaNeural", "hi": "hi-IN-Kavya:MAI-Voice-2",
          "ta": "ta-IN-PallaviNeural", "te": "te-IN-ShrutiNeural", "de": "de-DE-KatjaNeural"}
RATE = {"narrator": -6, "male": 2, "female": 0}   # base % ; a graver, epic narrator cadence
# Tamil/Telugu/Kannada neural voices are less native than DragonHD(en)/MAI-Voice-2(hi), so relax
# (slow) them for clearer word pronunciation and steadier sentence voicing.
SLOW_LANGS = {"ta", "te", "kn"}


def _rate(role, lang):
    r = RATE[role] - (9 if lang in SLOW_LANGS else 0)
    return f"+{r}%" if r > 0 else (f"{r}%" if r < 0 else "0%")

_FEM = re.compile(r"\b(queen|rani|she|her|woman|princess|empress|lady|maharani|begum)\b", re.I)
_BATTLE = re.compile(r"charge|cavalr|clash|battle|siege|storm|assault|fought|fight|sword|gun|"
                     r"cannon|\bwar\b|attack|fray|breach|arrows?|spear|lance|troops", re.I)
_SUSPENSE = re.compile(r"tense|wait|watch|surround|closing|silence|shadow|crept|escape|\bfell\b|"
                       r"last stand|grief|smoke|dusk|fear|betray|besieg|hunt|flee|dread|omen", re.I)


def mood_of(panel):
    blob = (panel.get("shot", "") + " " +
            " ".join((dl.get("text") or "") for dl in panel.get("dialogue", []) or []))
    if _BATTLE.search(blob):
        return "battle"
    if _SUSPENSE.search(blob):
        return "suspense"
    return "calm"


# Speak regnal Roman numerals as words so TTS doesn't read "Rajaraja Chola I" as the letter/pronoun.
_ORD = {"I": "the First", "II": "the Second", "III": "the Third", "IV": "the Fourth",
        "V": "the Fifth", "VI": "the Sixth", "VII": "the Seventh", "VIII": "the Eighth",
        "IX": "the Ninth", "X": "the Tenth"}
_REGNAL = re.compile(r'\b([A-Z][A-Za-z]{2,})\s+(VIII|VII|VI|IV|IX|III|II|V|X|I)\b')
_NOT_NAME = {"then", "when", "now", "and", "but", "so", "yet", "here", "there", "thus", "still",
             "he", "she", "they", "we", "you", "it", "as", "if", "or", "for", "nor", "later",
             "today", "once", "again", "though", "while", "since", "after", "before", "because",
             "these", "those", "this", "that", "why", "how", "who", "what", "where"}


def _expand_regnal(text):
    """'Rajaraja Chola I' -> 'Rajaraja Chola the First'. Leaves the pronoun 'I' (e.g. 'When I') alone."""
    def rep(m):
        prev, num = m.group(1), m.group(2)
        if num == "I" and prev.lower() in _NOT_NAME:
            return m.group(0)
        return f"{prev} {_ORD[num]}"
    return _REGNAL.sub(rep, text or "")


def _token():
    r = subprocess.run(["az", "account", "get-access-token", "--resource", CS_SCOPE,
                        "--query", "accessToken", "-o", "tsv"],
                       capture_output=True, text=True, shell=True, timeout=120)
    t = r.stdout.strip()
    if not t:
        raise RuntimeError("no AAD token; run az login")
    return t


def _make_cfg():
    cfg = speechsdk.SpeechConfig(auth_token=f"aad#{RID}#{_token()}", region=REGION)
    cfg.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio24Khz96KBitRateMonoMp3)
    return cfg


def _lang_of(voice):
    m = re.match(r"^([a-z]{2,3}-[A-Z]{2})", voice or "")
    return m.group(1) if m else "en-IN"


# Emotional delivery per mood. `nstyle`/`dstyle` = express-as style for narrator / character (hero
# speech); `pitch` + `rate` add an emotional contour that works even on voices without style support.
EMO = {
    "battle":   {"nstyle": "excited",  "dstyle": "angry",    "pitch": "+8%",  "rate": 6},
    "suspense": {"nstyle": "sad",      "dstyle": "sad",      "pitch": "-7%",  "rate": -7},
    "triumph":  {"nstyle": "hopeful",  "dstyle": "hopeful",  "pitch": "+6%",  "rate": 2},
    "spirit":   {"nstyle": "hopeful",  "dstyle": "hopeful",  "pitch": "+3%",  "rate": -4},
    "calm":     {"nstyle": "friendly", "dstyle": "friendly", "pitch": "+2%",  "rate": 0},
}


def _emo(role, mood):
    m = EMO.get(mood or "calm", EMO["calm"])
    return (m["dstyle"] if role in ("male", "female") else m["nstyle"]), m["pitch"], m["rate"]


def _fmt_rate(n):
    return f"+{n}%" if n > 0 else (f"{n}%" if n < 0 else "0%")


def _ssml(text, voice, rate, style=None, pitch="0%"):
    body = f'<prosody rate="{rate}" pitch="{pitch}">{html.escape(text.strip())}</prosody>'
    if style:
        body = f'<mstts:express-as style="{style}" styledegree="1.8">{body}</mstts:express-as>'
    return (f'<speak version="1.0" xmlns:mstts="https://www.w3.org/2001/mstts" '
            f'xml:lang="{_lang_of(voice)}"><voice name="{voice}">{body}</voice></speak>')


def lead_gender(figkey):
    e = C.registry_get(figkey) or {}
    bible = C.load_json(C.CHARS / f"{figkey}.json", {})
    blob = (f"{e.get('display_name','')} {e.get('ref_desc','')} "
            f"{bible.get('one_line','')} {bible.get('appearance','')}")
    return "female" if _FEM.search(blob) else "male"


def role_of(line_type, gender):
    return "narrator" if line_type in ("narration", "caption") else gender


def voice_for(role, lang):
    table = {"narrator": NARR, "male": MALE, "female": FEMALE}[role]
    return table.get(lang, table["en"]), _rate(role, lang)


def voice_multi(text, outdir, key, langs, role="narrator", tok=None, mood="calm"):
    """Translate `text` into each language (English source) and synthesise one clip per language
    (Hindi uses MAI-Voice-2 via the voice map). `mood` drives the emotional delivery. Writes
    <key>_<lang>.mp3/.json into `outdir`. Returns (text_map, words_map, tok). Skips existing clips."""
    import translate
    import pathlib as _p
    outdir = _p.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    text = _expand_regnal(text)
    syn = None
    text_map, words_map = {}, {}
    for lg in langs:
        if lg == "en":
            txt = text
        else:
            tr, tok = translate.translate_lines([text], lg, tok)
            txt = (tr[0] if tr else text)
        text_map[lg] = txt
        mp3, wj = outdir / f"{key}_{lg}.mp3", outdir / f"{key}_{lg}.json"
        if mp3.exists() and wj.exists():
            words_map[lg] = C.load_json(wj, {}).get("words", [])
            continue
        if syn is None:
            syn = Synth()
        v, rate = voice_for(role, lg)
        print(f"    voice {lg} {key} [{role}/{mood}] {v}", flush=True)
        w = syn.say(txt, mp3, v, rate, mood=mood, role=role)
        C.save_json(wj, {"words": w})
        words_map[lg] = w
    return text_map, words_map, tok


class Synth:
    """Holds a SpeechConfig, refreshing the token/config on cancellation."""

    def __init__(self):
        self.cfg = _make_cfg()

    def say(self, text, out_mp3, voice, rate, mood=None, role="narrator", tries=4):
        style, pitch, rdelta = _emo(role, mood)
        if "MAI-Voice" in (voice or ""):
            style = None    # MAI voices are flaky with express-as (0-byte turns); use pitch/rate only
        base = 0
        m = re.match(r"([+-]?\d+)", str(rate))
        if m:
            base = int(m.group(1))
        frate = _fmt_rate(base + rdelta)
        for i in range(1, tries + 1):
            words = []

            def on_wb(e):
                if e.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Punctuation:
                    return
                d = e.duration
                dur = d.total_seconds() * 1000 if hasattr(d, "total_seconds") else d / 10000
                words.append({"w": e.text, "t": round(e.audio_offset / 10000, 1),
                              "d": round(dur, 1)})

            audio = speechsdk.audio.AudioOutputConfig(filename=str(out_mp3))
            s = speechsdk.SpeechSynthesizer(speech_config=self.cfg, audio_config=audio)
            s.synthesis_word_boundary.connect(on_wb)
            use_style = style if i <= 2 else None   # drop express-as if the voice rejects the style
            r = s.speak_ssml_async(_ssml(text, voice, frate, style=use_style, pitch=pitch)).get()
            if r.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return words
            det = getattr(r, "cancellation_details", None)
            print(f"    TTS cancel (try {i}/{tries}): {det.reason if det else '?'} "
                  f"{det.error_details if det else ''}", flush=True)
            self.cfg = _make_cfg()  # refresh token
            time.sleep(2 * i)
        return []


def voice_episode(eid, langs, force=False):
    story = C.load_json(C.APP / "data" / f"{eid}.storyboard.json", None)
    if not story:
        sys.exit(f"no storyboard for {eid}")
    rec = C.load_json(C.APP / "data" / f"{eid}.json", {})
    gender = lead_gender(C.slug(rec.get("figure", eid)))
    syn = Synth()

    panels_out = []
    for p in story.get("panels", []):
        pid = p["id"]
        art = C.APP / "assets" / eid / "img" / f"{pid}.png"
        if not art.exists():
            continue
        lines = []
        pmood = mood_of(p)
        for i, dl in enumerate(p.get("dialogue", []) or []):
            role = role_of(dl.get("type", "speech"), gender)
            text, audio, words = {}, {}, {}
            for lg in langs:
                txt = (dl.get("i18n", {}).get(lg) if lg != "en" else dl.get("text", "")) or ""
                txt = _expand_regnal(txt)
                text[lg] = txt
                if not txt.strip():
                    continue
                outdir = C.APP / "assets" / eid / "audio" / lg
                outdir.mkdir(parents=True, exist_ok=True)
                mp3 = outdir / f"{pid}_{i}.mp3"
                wj = outdir / f"{pid}_{i}.json"
                if mp3.exists() and wj.exists() and not force:
                    words[lg] = C.load_json(wj, {}).get("words", [])
                else:
                    voice, rate = voice_for(role, lg)
                    print(f"  tts {lg} {pid}_{i} [{role}/{pmood}] {voice}", flush=True)
                    w = syn.say(txt, mp3, voice, rate, mood=pmood, role=role)
                    C.save_json(wj, {"words": w})
                    words[lg] = w
                audio[lg] = f"assets/{eid}/audio/{lg}/{pid}_{i}.mp3"
            lines.append({"type": dl.get("type", "speech"), "role": role,
                          "text": text, "audio": audio, "words": words})
        panels_out.append({"id": pid, "art": f"assets/{eid}/img/{pid}.png",
                           "shot": p.get("shot", ""), "mood": mood_of(p), "lines": lines})

    manifest = {"id": eid, "title": rec.get("title", eid), "title_i18n": story.get("title_i18n", {}),
                "figure": rec.get("figure", ""), "era": rec.get("era", ""),
                "moral": rec.get("moral", ""), "langs": langs, "panels": panels_out}
    C.save_json(C.APP / "data" / f"{eid}.player.json", manifest)
    print(f"DONE voice {eid}: {len(panels_out)} panels x {len(langs)} langs -> {eid}.player.json",
          flush=True)
    return manifest


def revoice_manifest(eid, langs=("en", "hi"), force=True):
    """Regenerate every audio clip already listed in <eid>.player.json IN PLACE with emotional
    delivery (mood from each scene, role from each line), refreshing word timings — WITHOUT
    rebuilding the manifest, so intro / action / montage inserts are preserved."""
    pj = C.APP / "data" / f"{eid}.player.json"
    man = C.load_json(pj, None)
    if not man:
        sys.exit(f"no player manifest for {eid}")
    syn = Synth()
    n = 0
    for p in man.get("panels", []):
        mood = p.get("mood") or "calm"
        for ln in p.get("lines", []):
            role = ln.get("role", "narrator")
            for lg in langs:
                txt = _expand_regnal((ln.get("text", {}) or {}).get(lg, ""))
                rel = (ln.get("audio", {}) or {}).get(lg, "")
                if not (txt and txt.strip() and rel):
                    continue
                ln.setdefault("text", {})[lg] = txt
                mp3 = C.APP / rel
                if not force and mp3.exists():
                    continue
                mp3.parent.mkdir(parents=True, exist_ok=True)
                v, rate = voice_for(role, lg)
                w = syn.say(txt, mp3, v, rate, mood=mood, role=role)
                ln.setdefault("words", {})[lg] = w
                n += 1
        print(f"  revoiced {p.get('id')} [{mood}]", flush=True)
    C.save_json(pj, man)
    print(f"REVOICE {eid}: {n} clips re-voiced with emotion", flush=True)
    return man


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eid")
    ap.add_argument("--langs", nargs="*", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--revoice", action="store_true",
                    help="re-voice the existing player.json in place with emotion (keeps inserts)")
    a = ap.parse_args()
    ep = C.find_episode(a.eid)
    eid = ep["id"] if ep else a.eid
    if a.revoice:
        revoice_manifest(eid, a.langs or ("en", "hi"), force=True)
    else:
        voice_episode(eid, a.langs or C.LANGS, force=a.force)


if __name__ == "__main__":
    main()
