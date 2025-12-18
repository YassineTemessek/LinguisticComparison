from __future__ import annotations

DEFAULT_SONAR_LANG_MAP: dict[str, str] = {
    # Best-effort defaults. Override per corpus with `@<sonar_lang>` in the CLI.
    "ar": "arb_Arab",
    "ara": "arb_Arab",
    "arb": "arb_Arab",
    "en": "eng_Latn",
    "eng": "eng_Latn",
    "fr": "fra_Latn",
    "fra": "fra_Latn",
    "de": "deu_Latn",
    "deu": "deu_Latn",
    "la": "lat_Latn",
    "lat": "lat_Latn",
    "grc": "grc_Grek",
    "el": "ell_Grek",
    "ell": "ell_Grek",
    "he": "heb_Hebr",
    "heb": "heb_Hebr",
    # Syriac / Aramaic variants differ by dataset; override when needed.
    "syr": "syc_Syrc",
    "syc": "syc_Syrc",
}


def resolve_sonar_lang(lang: str, sonar_lang_override: str | None) -> str:
    if sonar_lang_override:
        return sonar_lang_override
    key = (lang or "").strip().lower()
    if not key:
        raise ValueError("Missing `lang` for SONAR; provide `<lang>` and/or `@<sonar_lang>`.")
    if key in DEFAULT_SONAR_LANG_MAP:
        return DEFAULT_SONAR_LANG_MAP[key]
    raise ValueError(
        f"Unknown SONAR language mapping for lang={lang!r}. "
        "Provide an explicit SONAR code using `@<sonar_lang>` (e.g., `eng_Latn`, `arb_Arab`)."
    )
