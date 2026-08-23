# SPDX-License-Identifier: GPL-3.0-or-later
"""Testes da resolução de tema (sem QApplication ativo)."""

from __future__ import annotations

from macropad import theme


def test_default_setting_is_system():
    assert theme.DEFAULT_SETTING == theme.THEME_SYSTEM == "system"


def test_resolve_mode_passthrough():
    assert theme.resolve_mode("dark") == "dark"
    assert theme.resolve_mode("light") == "light"


def test_resolve_mode_unknown_falls_back_to_default_theme():
    assert theme.resolve_mode("chartreuse") == theme.DEFAULT_THEME


def test_resolve_system_without_app_falls_back():
    # Sem QApplication instanciado, detect_system_mode cai no tema padrão.
    assert theme.resolve_mode("system") in theme.PALETTES
    assert theme.detect_system_mode() == theme.DEFAULT_THEME


def test_stylesheet_for_every_mode_is_nonempty():
    for mode in ("system", "dark", "light"):
        css = theme.stylesheet_for(mode)
        assert isinstance(css, str) and css.strip()


def test_palettes_have_both_themes():
    assert set(theme.PALETTES) == {"dark", "light"}
