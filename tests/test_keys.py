# SPDX-License-Identifier: GPL-3.0-or-later
"""Testes do catálogo de teclas e do reconhecimento de ações."""

from __future__ import annotations

import pytest

from macropad import keys


@pytest.mark.parametrize("name", ["play", "volumeup", "mute", "PLAY", " next "])
def test_is_media_accepts_media_keys(name):
    assert keys.is_media(name)


@pytest.mark.parametrize("name", ["a", "ctrl", "f13", "click(left)"])
def test_is_media_rejects_non_media(name):
    assert not keys.is_media(name)


def test_media_alias_prev():
    assert keys.normalize_media("prev") == "previous"
    assert keys.is_media("prev")


@pytest.mark.parametrize(
    "alias,canonical",
    [("opt", "alt"), ("cmd", "win"), ("ropt", "ralt"), ("rcmd", "rwin")],
)
def test_modifier_aliases(alias, canonical):
    assert keys.normalize_modifier(alias) == canonical


def test_normalize_modifier_passthrough():
    assert keys.normalize_modifier("CTRL") == "ctrl"


@pytest.mark.parametrize("expr", ["<0>", "<110>", "<255>"])
def test_is_custom_code_valid(expr):
    assert keys.is_custom_code(expr)


@pytest.mark.parametrize("expr", ["<256>", "<-1>", "<abc>", "110", "<>"])
def test_is_custom_code_invalid(expr):
    assert not keys.is_custom_code(expr)


@pytest.mark.parametrize("expr", ["click(left)", "wheel(-1)", "move(5,0)", "drag(left,0,5)"])
def test_is_mouse(expr):
    assert keys.is_mouse(expr)


def test_is_mouse_rejects_plain_key():
    assert not keys.is_mouse("ctrl-c")


def test_known_key():
    assert keys.is_known_key("a")
    assert keys.is_known_key("f24")
    assert not keys.is_known_key("nope")


def test_all_keys_has_no_duplicates():
    assert len(keys.ALL_KEYS) == len(set(keys.ALL_KEYS))
