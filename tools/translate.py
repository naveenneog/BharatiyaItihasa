#!/usr/bin/env python3
"""Translate a comic storyboard's dialogue + captions + title into the app languages.

The panel ART is generated text-free, so translation only touches the lettering layer: we add
an `i18n` map to every dialogue item and `title_i18n` / `subtitle_i18n` to the storyboard, then
the (Chromium) letterer renders per-language pages. gpt-4o does the translation, returning short,
punchy comic-lettering-style lines in the target script.
"""
import json
import aiclient as ai

# app languages (mirrors common.LANGS); en is the source
LANG_NAMES = {"en": "English", "hi": "Hindi", "kn": "Kannada",
              "ta": "Tamil", "te": "Telugu", "de": "German"}
LANG_NATIVE = {"en": "English", "hi": "\u0939\u093f\u0928\u094d\u0926\u0940",
               "kn": "\u0c95\u0ca8\u0ccd\u0ca8\u0ca1", "ta": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd",
               "te": "\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41", "de": "Deutsch"}

_SYS = ("You are a professional translator for a children's HISTORICAL comic book about Indian "
        "history (anime-style action). Translate each English line into {LANG}, written in its "
        "native script. Keep every line SHORT, natural and punchy like real comic-book "
        "lettering/dialogue \u2014 not literal, formal or verbose. Transliterate names of people "
        "and places naturally into the target script. Return STRICT JSON only: "
        '{"t": [ ... translations, SAME order and SAME count as the input ... ]}.')


def translate_lines(lines, lang, tok=None, tries=2):
    """Translate a list of English strings into `lang`. Returns (list, tok)."""
    if lang == "en" or not lines:
        return list(lines), tok
    sys = _SYS.replace("{LANG}", LANG_NAMES.get(lang, lang))
    user = json.dumps({"lines": lines}, ensure_ascii=False)
    for _ in range(tries):
        out, tok = ai.chat_json(sys, user, tok=tok, max_tokens=3500)
        t = out.get("t") or out.get("translations") or []
        if isinstance(t, list) and len(t) == len(lines):
            return [str(x) for x in t], tok
    # fallback: pad/truncate to keep alignment (better a stray English line than a crash)
    t = [str(x) for x in (t if isinstance(t, list) else [])]
    t = (t + list(lines))[:len(lines)]
    return t, tok


def translate_storyboard(story, title, subtitle, langs, tok=None):
    """Mutate `story` in place: add title_i18n, subtitle_i18n and per-dialogue i18n maps for
    each language. One gpt-4o call per non-English language. Returns tok."""
    lines, idx = [], {}

    def add(key, txt):
        idx[key] = len(lines)
        lines.append(txt or "")

    add("title", title)
    add("subtitle", subtitle)
    for pi, p in enumerate(story.get("panels", [])):
        for di, dl in enumerate(p.get("dialogue", []) or []):
            t = (dl.get("text") or "").strip()
            if t:
                add((pi, di), t)

    story.setdefault("title_i18n", {})["en"] = title
    story.setdefault("subtitle_i18n", {})["en"] = subtitle
    dlg_keys = [k for k in idx if isinstance(k, tuple)]
    for lg in langs:
        if lg == "en":
            continue
        have = story["title_i18n"].get(lg) and all(
            story["panels"][pi]["dialogue"][di].get("i18n", {}).get(lg) for pi, di in dlg_keys)
        if have:  # already translated (keeps re-letter free)
            continue
        tr, tok = translate_lines(lines, lg, tok)
        story["title_i18n"][lg] = tr[idx["title"]]
        story["subtitle_i18n"][lg] = tr[idx["subtitle"]]
        for pi, p in enumerate(story.get("panels", [])):
            for di, dl in enumerate(p.get("dialogue", []) or []):
                key = (pi, di)
                if key in idx:
                    dl.setdefault("i18n", {})[lg] = tr[idx[key]]
    return tok
