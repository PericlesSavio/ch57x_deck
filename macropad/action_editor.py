# SPDX-License-Identifier: GPL-3.0-or-later
"""Editor de uma ação de tecla/knob.

Três modos:
- Teclado: modificadores + tecla, com até 5 passos encadeados (macro).
- Mídia: uma tecla de mídia isolada (o firmware não aceita modificadores aqui).
- Avançado: expressão livre no dialeto do firmware (mouse, <código>, etc.).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from . import keys as keycat
from .i18n import tr
from .keyboard_widget import KeyboardWidget

_MAX_CHORD = 5  # limite do firmware para acordes encadeados


class ActionEditor(QWidget):
    """Edita a ação da tecla/knob selecionada e emite `action_changed`."""

    action_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._updating = False

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_keyboard_tab(), tr("tab_keyboard"))
        self._tabs.addTab(self._build_media_tab(), tr("tab_media"))
        self._tabs.addTab(self._build_advanced_tab(), tr("tab_advanced"))

        clear = QPushButton(tr("btn_clear"))
        clear.clicked.connect(self._clear)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tabs, stretch=1)
        layout.addWidget(clear, alignment=Qt.AlignmentFlag.AlignRight)

    # ------------------------------------------------------------------
    # Abas
    # ------------------------------------------------------------------

    def _build_keyboard_tab(self) -> QWidget:
        tab = QWidget()

        self._kb = KeyboardWidget()
        self._kb.changed.connect(self._keyboard_changed)

        hint = QLabel(tr("kb_hint"))
        hint.setProperty("role", "dim")
        hint.setWordWrap(True)

        add_step = QPushButton(tr("btn_add_step"))
        add_step.clicked.connect(self._add_chord_step)

        self._chord_list = QListWidget()
        self._chord_list.setToolTip(tr("chord_tooltip"))

        remove_step = QPushButton(tr("btn_remove_step"))
        remove_step.clicked.connect(self._remove_chord_step)

        layout = QVBoxLayout(tab)
        # Teclado à esquerda; coluna de macro (botões + lista de passos) à
        # direita, com a mesma altura do teclado.
        row = QHBoxLayout()
        row.addWidget(self._kb, stretch=1)
        macro_col = QVBoxLayout()
        # Largura justa para os rótulos completos dos botões.
        for widget in (add_step, remove_step, self._chord_list):
            widget.setMaximumWidth(235)
            macro_col.addWidget(widget)
        macro_col.setStretchFactor(self._chord_list, 1)
        row.addLayout(macro_col)
        layout.addLayout(row, stretch=1)
        layout.addWidget(hint)
        return tab

    def _build_media_tab(self) -> QWidget:
        tab = QWidget()
        self._media_combo = QComboBox()
        self._media_combo.addItem(tr("combo_none"), "")
        for key in keycat.MEDIA_KEYS:
            self._media_combo.addItem(key, key)
        self._media_combo.currentIndexChanged.connect(self._media_changed)

        hint = QLabel(tr("media_hint"))
        hint.setProperty("role", "dim")

        layout = QVBoxLayout(tab)
        layout.addWidget(self._media_combo)
        layout.addWidget(hint)
        layout.addStretch()
        return tab

    def _build_advanced_tab(self) -> QWidget:
        tab = QWidget()
        self._advanced_edit = QLineEdit()
        self._advanced_edit.setPlaceholderText(tr("adv_placeholder"))
        self._advanced_edit.textEdited.connect(self._advanced_changed)

        hint = QLabel(tr("adv_hint"))
        hint.setProperty("role", "dim")

        layout = QVBoxLayout(tab)
        layout.addWidget(self._advanced_edit)
        layout.addWidget(hint)
        layout.addStretch()
        return tab

    # ------------------------------------------------------------------
    # Estado -> widgets
    # ------------------------------------------------------------------

    def set_keyboard_layout(self, layout_id: str) -> None:
        """Re-rotula o teclado visual para o layout físico escolhido."""
        self._kb.apply_layout(layout_id)

    def set_action(self, action: str) -> None:
        """Carrega uma ação existente e escolhe a aba adequada."""
        self._updating = True
        try:
            self._reset_widgets()
            action = action.strip()
            if not action:
                self._tabs.setCurrentIndex(0)
                return

            if keycat.is_media(action):
                index = self._media_combo.findData(keycat.normalize_media(action))
                self._media_combo.setCurrentIndex(max(index, 0))
                self._tabs.setCurrentIndex(1)
                return

            if self._try_load_keyboard(action):
                self._tabs.setCurrentIndex(0)
                return

            self._advanced_edit.setText(action)
            self._tabs.setCurrentIndex(2)
        finally:
            self._updating = False

    def _reset_widgets(self) -> None:
        self._kb.clear_state()
        self._chord_list.clear()
        self._media_combo.setCurrentIndex(0)
        self._advanced_edit.clear()

    def _try_load_keyboard(self, action: str) -> bool:
        """Tenta interpretar como acorde(s) de teclado simples."""
        steps = [p.strip() for p in action.split(",") if p.strip()]
        parsed = []
        for step in steps:
            parts = [keycat.normalize_modifier(p) for p in step.split("-")]
            *mods, key = parts
            if key and not self._kb.has_key(key):
                return False
            if any(not self._kb.has_modifier(m) for m in mods):
                return False
            parsed.append((mods, key))

        first_mods, first_key = parsed[0]
        self._kb.set_state(first_mods, first_key or None)

        for mods, key in parsed[1:]:
            self._chord_list.addItem("-".join([*mods, key] if key else mods))
        return True

    # ------------------------------------------------------------------
    # Widgets -> ação
    # ------------------------------------------------------------------

    def _current_chord(self) -> str:
        mods = self._kb.active_modifiers()
        key = self._kb.selected_key() or ""
        if not key and not mods:
            return ""
        return "-".join([*mods, key] if key else mods)

    def _emit_keyboard(self) -> None:
        steps = [self._current_chord()]
        steps += [
            self._chord_list.item(i).text() for i in range(self._chord_list.count())
        ]
        steps = [s for s in steps if s]
        self.action_changed.emit(",".join(steps))

    def _keyboard_changed(self) -> None:
        if not self._updating:
            self._emit_keyboard()

    def _add_chord_step(self) -> None:
        chord = self._current_chord()
        if not chord:
            return
        # A lista guarda os passos seguintes; o atual continua nos widgets.
        if 1 + self._chord_list.count() >= _MAX_CHORD:
            return
        self._chord_list.addItem(chord)
        self._kb.clear_state()
        self._emit_keyboard()

    def _remove_chord_step(self) -> None:
        row = self._chord_list.currentRow()
        if row >= 0:
            self._chord_list.takeItem(row)
            self._emit_keyboard()

    def _media_changed(self) -> None:
        if not self._updating:
            self.action_changed.emit(self._media_combo.currentData() or "")

    def _advanced_changed(self, text: str) -> None:
        if not self._updating:
            self.action_changed.emit(text.strip())

    def _clear(self) -> None:
        self._updating = True
        self._reset_widgets()
        self._updating = False
        self.action_changed.emit("")
