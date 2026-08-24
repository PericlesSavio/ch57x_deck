# SPDX-License-Identifier: GPL-3.0-or-later
"""Testes de completude e formatação das traduções."""

from __future__ import annotations

import pytest
import yaml

from macropad import i18n


@pytest.mark.parametrize("lang", ["pt_BR", "en", "es"])
def test_every_string_has_all_languages(lang):
    missing = [key for key, entry in i18n.STRINGS.items() if lang not in entry]
    assert not missing, f"faltam traduções em {lang}: {missing}"


def test_locale_files_exist_with_matching_keys():
    """Os YAMLs de cada idioma existem e cobrem exatamente as mesmas chaves."""
    keys_by_lang = {}
    for lang in i18n.LANGUAGES:
        path = i18n._LOCALES_DIR / f"{lang}.yaml"
        assert path.is_file(), f"falta o arquivo {lang}.yaml"
        keys_by_lang[lang] = set(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    base = keys_by_lang["en"]
    for lang, keys in keys_by_lang.items():
        assert keys == base, (
            f"{lang}.yaml diverge — só nele: {keys - base}; faltando: {base - keys}"
        )


def test_default_language_is_pt_br():
    assert i18n.DEFAULT == "pt_BR"
    assert set(i18n.LANGUAGES) == {"pt_BR", "en", "es"}


def test_tr_falls_back_to_key_when_missing():
    assert i18n.tr("__inexistente__") == "__inexistente__"


def test_tr_formats_placeholders():
    # layer_tab existe em todos os idiomas e usa {n}
    assert "7" in i18n.tr("layer_tab", n=7)


def test_variant_and_theme_keys_present():
    for key in ("menu_device", "menu_keyboard", "theme_system", "kbd_abnt2"):
        assert key in i18n.STRINGS
