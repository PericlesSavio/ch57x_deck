# SPDX-License-Identifier: GPL-3.0-or-later
"""Testes dos layouts físicos de teclado.

Importa a tabela `_ROWS` do teclado visual (só a estrutura de dados; nenhum
widget é instanciado), então roda sem display e sem QApplication.
"""

from __future__ import annotations

from macropad import layouts
from macropad.keyboard_widget import _ROWS

# Nomes HID que de fato têm um botão no teclado visual.
KEY_NAMES = {
    name for row in _ROWS for (name, _label, _width) in row if name is not None
}


def test_default_layout_is_us_and_has_no_overrides():
    assert layouts.DEFAULT_LAYOUT == "us"
    assert layouts.KEYBOARD_LAYOUTS["us"] == {}


def test_layout_order_matches_table():
    assert set(layouts.LAYOUT_ORDER) == set(layouts.KEYBOARD_LAYOUTS)


def test_every_override_targets_a_real_key():
    """Um override para um nome inexistente seria silenciosamente ignorado."""
    for layout_id, overrides in layouts.KEYBOARD_LAYOUTS.items():
        orphans = sorted(name for name in overrides if name not in KEY_NAMES)
        assert not orphans, f"{layout_id}: nomes sem tecla no teclado: {orphans}"


def test_labels_for_unknown_layout_is_empty():
    assert layouts.labels_for("klingon") == {}


def test_abnt2_maps_semicolon_to_cedilla():
    assert layouts.KEYBOARD_LAYOUTS["abnt2"]["semicolon"] == "Ç"


def test_azerty_swaps_letter_positions():
    fr = layouts.KEYBOARD_LAYOUTS["fr"]
    assert fr["q"] == "A"
    assert fr["a"] == "Q"
    assert fr["w"] == "Z"
