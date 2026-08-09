"""Teclado visual clicável para escolher a combinação de teclas.

Desenha um teclado completo (fileira F, F13–F24, bloco principal, navegação e
numérico). Modificadores são botões de alternância; clicar numa tecla comum a
seleciona (clicar de novo desmarca). O widget emite `changed` a cada alteração.

Os nomes seguem o dialeto do firmware (posições HID, layout US) — ver keys.py.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QPushButton, QSizePolicy, QWidget

from . import keys as keycat

# Unidade de largura: 1u = 4 colunas do grid (permite larguras de 0.25u).
_U = 4

# Cada linha: lista de (nome no firmware | None para vão, rótulo, largura em u).
# None como nome cria um espaço vazio.
#
# Grade horizontal comum a todas as fileiras (total 22.75u):
#   bloco principal 0–15u · vão 0.5u · navegação 15.5–18.5u ·
#   vão 0.25u · teclado numérico 18.75–22.75u
_ROWS: list[list[tuple[str | None, str, float]]] = [
    # Fileira F
    [
        ("escape", "Esc", 1),
        (None, "", 0.5),
        ("f1", "F1", 1), ("f2", "F2", 1), ("f3", "F3", 1), ("f4", "F4", 1),
        ("f5", "F5", 1), ("f6", "F6", 1), ("f7", "F7", 1), ("f8", "F8", 1),
        ("f9", "F9", 1), ("f10", "F10", 1), ("f11", "F11", 1), ("f12", "F12", 1),
        ("printscreen", "Prt", 1),
        (None, "", 1.0),
        ("insert", "Ins", 1), ("home", "Home", 1), ("pageup", "PgUp", 1),
        (None, "", 0.25),
        ("numlock", "Num", 1), ("numpadslash", "/", 1),
        ("numpadasterisk", "*", 1), ("numpadminus", "-", 1),
    ],
    # F13–F24: as teclas "fantasma" ideais para atalhos de sistema
    [
        ("f13", "F13", 1.25), ("f14", "F14", 1.25), ("f15", "F15", 1.25),
        ("f16", "F16", 1.25), ("f17", "F17", 1.25), ("f18", "F18", 1.25),
        ("f19", "F19", 1.25), ("f20", "F20", 1.25), ("f21", "F21", 1.25),
        ("f22", "F22", 1.25), ("f23", "F23", 1.25), ("f24", "F24", 1.25),
        (None, "", 0.5),
        ("delete", "Del", 1), ("end", "End", 1), ("pagedown", "PgDn", 1),
        (None, "", 0.25),
        ("numpad7", "7", 1), ("numpad8", "8", 1),
        ("numpad9", "9", 1), ("numpadplus", "+", 1),
    ],
    # Números
    [
        ("grave", "`", 1),
        ("1", "1", 1), ("2", "2", 1), ("3", "3", 1), ("4", "4", 1),
        ("5", "5", 1), ("6", "6", 1), ("7", "7", 1), ("8", "8", 1),
        ("9", "9", 1), ("0", "0", 1),
        ("minus", "-", 1), ("equal", "=", 1),
        ("backspace", "⌫", 2),
        (None, "", 3.75),
        ("numpad4", "4", 1), ("numpad5", "5", 1),
        ("numpad6", "6", 1), ("numpadequal", "=", 1),
    ],
    # QWERTY
    [
        ("tab", "Tab", 1.5),
        ("q", "Q", 1), ("w", "W", 1), ("e", "E", 1), ("r", "R", 1),
        ("t", "T", 1), ("y", "Y", 1), ("u", "U", 1), ("i", "I", 1),
        ("o", "O", 1), ("p", "P", 1),
        ("leftbracket", "[", 1), ("rightbracket", "]", 1),
        ("backslash", "\\", 1.5),
        (None, "", 3.75),
        ("numpad1", "1", 1), ("numpad2", "2", 1),
        ("numpad3", "3", 1), ("numpadenter", "⏎", 1),
    ],
    # Home row
    [
        ("capslock", "Caps", 1.75),
        ("a", "A", 1), ("s", "S", 1), ("d", "D", 1), ("f", "F", 1),
        ("g", "G", 1), ("h", "H", 1), ("j", "J", 1), ("k", "K", 1),
        ("l", "L", 1),
        ("semicolon", ";", 1), ("quote", "'", 1),
        ("enter", "Enter ⏎", 2.25),
        (None, "", 3.75),
        ("numpad0", "0", 2), ("numpaddot", ".", 1),
        (None, "", 1),
    ],
    # Shift row
    [
        ("shift", "Shift", 2.25),
        ("z", "Z", 1), ("x", "X", 1), ("c", "C", 1), ("v", "V", 1),
        ("b", "B", 1), ("n", "N", 1), ("m", "M", 1),
        ("comma", ",", 1), ("dot", ".", 1), ("slash", "/", 1),
        ("rshift", "Shift", 2.75),
        (None, "", 1.5),
        ("up", "↑", 1),
        (None, "", 5.25),
    ],
    # Modificadores
    [
        ("ctrl", "Ctrl", 1.25), ("win", "Win", 1.25), ("alt", "Alt", 1.25),
        ("space", "␣ espaço", 6.25),
        ("ralt", "AltGr", 1.25), ("rwin", "Win", 1.25),
        ("application", "☰", 1.25), ("rctrl", "Ctrl", 1.25),
        (None, "", 0.5),
        ("left", "←", 1), ("down", "↓", 1), ("right", "→", 1),
        (None, "", 4.25),
    ],
]


class KeyboardWidget(QWidget):
    """Teclado clicável: modificadores alternáveis + uma tecla selecionada."""

    changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._updating = False
        self._selected: str | None = None
        self._mod_buttons: dict[str, QPushButton] = {}
        self._key_buttons: dict[str, QPushButton] = {}

        # O teclado absorve o espaço vertical disponível na aba.
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(2)

        total_cols = 0
        for row_index, row in enumerate(_ROWS):
            col = 0
            for name, label, width in row:
                span = round(width * _U)
                if name is not None:
                    self._add_key(grid, row_index, col, span, name, label)
                col += span
            total_cols = max(total_cols, col)

        for c in range(total_cols):
            grid.setColumnStretch(c, 1)
            grid.setColumnMinimumWidth(c, 6)
        for r in range(len(_ROWS)):
            grid.setRowStretch(r, 1)

    def _add_key(
        self, grid: QGridLayout, row: int, col: int, span: int, name: str, label: str
    ) -> None:
        btn = QPushButton(label)
        btn.setProperty("role", "kb")
        btn.setCheckable(True)
        btn.setMinimumHeight(30)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn.setToolTip(name)
        if name in keycat.MODIFIERS:
            btn.toggled.connect(self._modifier_toggled)
            self._mod_buttons[name] = btn
        else:
            btn.clicked.connect(lambda _=False, n=name: self._key_clicked(n))
            self._key_buttons[name] = btn
        grid.addWidget(btn, row, col, 1, span)

    # ------------------------------------------------------------------
    # Interação
    # ------------------------------------------------------------------

    def _modifier_toggled(self) -> None:
        if not self._updating:
            self.changed.emit()

    def _key_clicked(self, name: str) -> None:
        if self._selected == name:
            self._selected = None  # clicar de novo desmarca
        else:
            if self._selected:
                self._key_buttons[self._selected].setChecked(False)
            self._selected = name
        self._key_buttons[name].setChecked(self._selected == name)
        if not self._updating:
            self.changed.emit()

    # ------------------------------------------------------------------
    # Estado
    # ------------------------------------------------------------------

    def active_modifiers(self) -> list[str]:
        """Modificadores marcados, na ordem canônica do dialeto."""
        return [
            mod
            for mod in keycat.MODIFIERS
            if mod in self._mod_buttons and self._mod_buttons[mod].isChecked()
        ]

    def selected_key(self) -> str | None:
        return self._selected

    def has_modifier(self, name: str) -> bool:
        return name in self._mod_buttons

    def has_key(self, name: str) -> bool:
        return name in self._key_buttons

    def set_state(self, modifiers: list[str], key: str | None) -> None:
        """Aplica um estado sem emitir `changed`."""
        self._updating = True
        try:
            self.clear_state()
            for mod in modifiers:
                if mod in self._mod_buttons:
                    self._mod_buttons[mod].setChecked(True)
            if key and key in self._key_buttons:
                self._selected = key
                self._key_buttons[key].setChecked(True)
        finally:
            self._updating = False

    def clear_state(self) -> None:
        was_updating = self._updating
        self._updating = True
        try:
            for btn in self._mod_buttons.values():
                btn.setChecked(False)
            if self._selected:
                self._key_buttons[self._selected].setChecked(False)
            self._selected = None
        finally:
            self._updating = was_updating
