"""Internationalization (i18n) utilities for translations."""

import json
from pathlib import Path
from typing import Dict

# Translation cache
_translations: Dict[str, Dict[str, str]] = {}
_translations_dir = Path(__file__).parent.parent / "translations"


def load_translations(lang: str = "en") -> Dict[str, str]:
    """Load translations for a language."""
    if lang in _translations:
        return _translations[lang]
    
    # Validate and default to English if invalid
    if lang not in ["en", "hu", "de", "id", "zh", "hi", "es", "fr", "ar", "ru", "ko", "ja", "it", "rm", "ur", "bn", "th", "lo", "mn"]:
        lang = "en"
    
    translation_file = _translations_dir / f"{lang}.json"
    if not translation_file.exists():
        translation_file = _translations_dir / "en.json"
    
    try:
        with open(translation_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
            _translations[lang] = translations
            return translations
    except Exception:
        return {}

