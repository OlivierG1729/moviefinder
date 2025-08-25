
############################
# Language detection       #
#                          #
# Last update : 2025/08/25 #
############################

# services/i18n.py
# Détection de langue + traduction FR + badge HTML
# Dépendances : langdetect, deep-translator

# services/i18n.py
from __future__ import annotations
from typing import Optional, Tuple, List
from functools import lru_cache
import html
import re
import requests

# ── Détection locale (langdetect) ─────────────────────────────────────────────
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0  # stabiliser les résultats
except Exception:
    detect = None

# ── Provider de traduction (secours) ──────────────────────────────────────────
try:
    from deep_translator import GoogleTranslator
except Exception:
    GoogleTranslator = None

_LANG_LABELS = {
    "fr": "FR", "en": "EN", "es": "ES", "de": "DE", "it": "IT", "pt": "PT",
}

# ── Utils texte ───────────────────────────────────────────────────────────────
_TAG_RE = re.compile(r"<[^>]+>")  # pour enlever les balises HTML

def _strip_tags(s: str) -> str:
    return _TAG_RE.sub("", s)

def _normalize_text(t: str) -> str:
    if not isinstance(t, str):
        t = str(t)
    t = html.unescape(t).replace("\u200b", "")
    t = _strip_tags(t)
    t = t.strip()
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\s*\n\s*", "\n", t)
    return t

def _cmp_key(t: str) -> str:
    t = _normalize_text(t).casefold()
    t = re.sub(r"\s+", " ", t)
    return t

def _split_chunks(t: str, max_len: int = 450) -> List[str]:
    t = _normalize_text(t)
    if len(t) <= max_len:
        return [t]
    parts, cur, cur_len = [], [], 0
    for para in t.split("\n"):
        if not para:
            continue
        L = len(para) + 1
        if cur and cur_len + L > max_len:
            parts.append(" ".join(cur))
            cur, cur_len = [para], len(para)
        else:
            cur.append(para)
            cur_len += L
    if cur:
        parts.append(" ".join(cur))
    return parts

# ── Détection via API (fallback) ──────────────────────────────────────────────
@lru_cache(maxsize=2048)
def _remote_detect(text: str) -> Optional[str]:
    """
    Utilise l'API MyMemory pour obtenir la langue détectée (sans se fier à la traduction).
    """
    try:
        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text[:5000], "langpair": "auto|fr"},
            headers={"User-Agent": "MovieFinder/1.0"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        code = data.get("responseData", {}).get("detectedLanguage")
        if isinstance(code, str) and code:
            return code.lower()
    except Exception:
        pass
    return None

def detect_lang(text: Optional[str]) -> Optional[str]:
    """
    Essaie langdetect localement (si dispo), sinon fallback API MyMemory.
    Nettoie aussi HTML, joint les listes, compacte le texte.
    """
    if not text:
        return None
    if isinstance(text, list):
        text = " ".join([str(x) for x in text if x])
    text = _normalize_text(text)
    if not text:
        return None

    # 1) tentative locale
    if detect:
        try:
            code = detect(text)
            if isinstance(code, str) and code:
                return code.lower()
        except Exception:
            pass

    # 2) fallback réseau
    return _remote_detect(text)

# ── Traduction ────────────────────────────────────────────────────────────────
def _google_translate_chunk(s: str) -> Optional[str]:
    if not GoogleTranslator:
        return None
    try:
        return GoogleTranslator(source="auto", target="fr").translate(s)
    except Exception:
        return None

@lru_cache(maxsize=1024)
def _mymemory_translate_chunk(s: str) -> Optional[str]:
    try:
        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": s, "langpair": "auto|fr"},
            headers={"User-Agent": "MovieFinder/1.0"},
            timeout=12,
        )
        r.raise_for_status()
        data = r.json()
        t = data.get("responseData", {}).get("translatedText", "")
        return html.unescape(t) if t else None
    except Exception:
        return None

def _translate_long_text(text: str) -> str:
    """
    Essaie Google chunk par chunk, puis fallback MyMemory par chunk,
    sinon renvoie l'original.
    """
    chunks = _split_chunks(text, max_len=450)

    # 1) Google (si dispo)
    out: List[str] = []
    if GoogleTranslator:
        for c in chunks:
            t = _google_translate_chunk(c)
            out.append(t if t else c)
        joined = "\n\n".join(out).strip()
        if _cmp_key(joined) != _cmp_key(text):
            return joined

    # 2) MyMemory
    out = []
    for c in chunks:
        t = _mymemory_translate_chunk(c)
        out.append(t if t else c)
    return "\n\n".join(out).strip()

def translate_to_fr(text: str, *, force: bool = False) -> Tuple[str, bool, Optional[str]]:
    """
    Retourne (texte_traduit, ok, langue_source_detectee).
    - ok=True si la traduction est réellement différente
    - si force=True, on traduit même si détecté FR
    """
    if not text:
        return "", False, None

    src = detect_lang(text) or None
    if src == "fr" and not force:
        return text, False, "fr"

    normalized = _normalize_text(text)
    translated = _translate_long_text(normalized)
    ok = _cmp_key(translated) != _cmp_key(normalized)
    return translated, ok, (src or detect_lang(translated))


# ── Badge langue ──────────────────────────────────────────────────────────────
def lang_badge_html(sample_text: str) -> str:
    code = detect_lang(sample_text) or ""
    tag = _LANG_LABELS.get(code, (code.upper()[:2] if code else "??"))
    bg = "#e8f5e9" if tag == "FR" else "#e3f2fd" if tag == "EN" else "#f3e5f5"
    return f"<span style='background:{bg};border-radius:0.5rem;padding:0.15rem 0.5rem;'>{tag}</span>"
