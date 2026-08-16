import json
import os
from pathlib import Path

import streamlit as st

LOCALES_DIR = Path(__file__).parent / "locales"

SUPPORTED_LANGUAGES = {
    "tr": "🇹🇷 Türkçe",
    "en": "🇬🇧 English",
}

DEFAULT_LANGUAGE = "tr"


def _load_translations(lang: str) -> dict:
    file_path = LOCALES_DIR / f"{lang}.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


_translations_cache = {}


def get_translations(lang: str) -> dict:
    if lang not in _translations_cache:
        _translations_cache[lang] = _load_translations(lang)
    return _translations_cache[lang]


def get_current_language() -> str:
    if "lang" in st.session_state:
        return st.session_state["lang"]

    query_lang = st.query_params.get("lang")
    if query_lang in SUPPORTED_LANGUAGES:
        st.session_state["lang"] = query_lang
        return query_lang

    browser_lang = _detect_browser_language()
    if browser_lang in SUPPORTED_LANGUAGES:
        st.session_state["lang"] = browser_lang
        return browser_lang

    st.session_state["lang"] = DEFAULT_LANGUAGE
    return DEFAULT_LANGUAGE


def set_language(lang: str) -> None:
    if lang in SUPPORTED_LANGUAGES:
        st.session_state["lang"] = lang
        st.query_params["lang"] = lang


def t(key: str, lang: str = None, **kwargs) -> str:
    if lang is None:
        lang = get_current_language()
    translations = get_translations(lang)
    text = translations.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def _detect_browser_language() -> str:
    try:
        accept_language = st.context.headers.get("Accept-Language", "")
        if not accept_language:
            return DEFAULT_LANGUAGE

        parts = accept_language.split(",")
        for part in parts:
            lang = part.strip().split("-")[0].lower()
            if lang in SUPPORTED_LANGUAGES:
                return lang
    except Exception:
        pass
    return DEFAULT_LANGUAGE


def render_language_switcher() -> None:
    current_lang = get_current_language()
    options = list(SUPPORTED_LANGUAGES.values())
    index = list(SUPPORTED_LANGUAGES.keys()).index(current_lang)

    selected = st.radio(
        t("language"),
        options,
        index=index,
        key="language_selector",
    )

    for lang_code, label in SUPPORTED_LANGUAGES.items():
        if label == selected and lang_code != current_lang:
            set_language(lang_code)
            break
