
############################
# Language detection       #
#                          #
# Last update : 2025/08/25 #
############################

# services/i18n.py
# Détection de langue + traduction FR + badge HTML
# Dépendances : langdetect, deep-translator

from typing import Optional

try:
    from langdetect import detect
except Exception:
    detect = None

try:
    from deep_translator import GoogleTranslator
except Exception:
    GoogleTranslator = None

_LANG_LABELS = {
    "fr": "FR",
    "en": "EN",
    "es": "ES",
    "de": "DE",
    "it": "IT",
    "pt": "PT",
}

def detect_lang(text: Optional[str]) -> Optional[str]:
    if not text or not detect:
        return None
    try:
        code = detect(text)
        if not isinstance(code, str):
            return None
        return code.lower()
    except Exception:
        return None

def translate_to_fr(text: str) -> str:
    if not text:
        return ""
    if not GoogleTranslator:
        return text
    try:
        return GoogleTranslator(source="auto", target="fr").translate(text)
    except Exception:
        return text

def lang_badge_html(sample_text: str) -> str:
    code = detect_lang(sample_text) or ""
    tag = _LANG_LABELS.get(code, (code.upper()[:2] if code else "??"))
    # Couleurs simples : FR (vert clair), EN (bleu clair), autres (violet clair)
    if tag == "FR":
        bg = "#e8f5e9"
    elif tag == "EN":
        bg = "#e3f2fd"
    else:
        bg = "#f3e5f5"
    return f"<span style='background:{bg};border-radius:0.5rem;padding:0.15rem 0.5rem;'>{tag}</span>"
