# SPDX-License-Identifier: GPL-3.0-or-later
"""Testes do pacote de edição: desfazer/refazer, copiar/colar, duplicar camada.

Instancia a MainWindow real (offscreen) porque essa lógica vive na janela.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6.QtWidgets")
from PySide6.QtWidgets import QApplication  # noqa: E402

from macropad.main_window import MainWindow  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(app):
    win = MainWindow()
    win._select_button(0, 0)
    yield win
    win._device_timer.stop()


def cell(win, row=0, col=0):
    return win.config.get(win.current_layer, row, col)


def test_edit_then_undo_redo(window):
    original = cell(window)  # default: f13
    window._select_button(0, 0)
    window._action_edited("ctrl-c")
    assert cell(window) == "ctrl-c"
    window._undo()
    assert cell(window) == original
    window._redo()
    assert cell(window) == "ctrl-c"


def test_consecutive_edits_same_key_coalesce(window):
    window._select_button(0, 0)
    window._action_edited("a")
    window._action_edited("a-b")  # mesma tecla -> uma só entrada de desfazer
    assert len(window._undo_stack) == 1
    window._undo()
    assert cell(window) == "f13"  # volta ao original de uma vez


def test_edits_on_different_keys_are_separate(window):
    window._select_button(0, 0)
    window._action_edited("x")
    window._select_button(0, 1)
    window._action_edited("y")
    assert len(window._undo_stack) == 2
    window._undo()
    assert window.config.get(0, 0, 1) == "f14"  # desfez só a última (K2)
    assert window.config.get(0, 0, 0) == "x"


def test_copy_paste_action(window):
    window._select_button(0, 0)
    window._action_edited("ctrl-c,ctrl-v")
    window._copy_action()
    assert window._action_clipboard == "ctrl-c,ctrl-v"
    window._select_button(0, 1)
    window._paste_action()
    assert window.config.get(0, 0, 1) == "ctrl-c,ctrl-v"
    window._undo()
    assert window.config.get(0, 0, 1) == "f14"  # colar é desfazível


def test_copy_layer(window):
    window._layer_bar.setCurrentIndex(0)
    window._select_button(0, 0)
    window._action_edited("alt-f4")
    window._copy_layer_to(1)
    assert window.config.get(1, 0, 0) == "alt-f4"
    window._undo()
    assert window.config.get(1, 0, 0) == ""


def test_copy_layer_to_self_is_noop(window):
    before = len(window._undo_stack)
    window._copy_layer_to(window.current_layer)
    assert len(window._undo_stack) == before  # nada empilhado
