# SPDX-License-Identifier: GPL-3.0-or-later
"""Área de teste: captura e exibe o que o macropad envia de fato.

O usuário clica no campo e aperta as teclas físicas; cada evento recebido
(tecla, combinação, roda ou clique) é registrado numa linha. Serve para
conferir o mapeamento sem sair do app.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from .i18n import tr

# Modificadores sozinhos não geram linha — só quando acompanham uma tecla.
_MODIFIER_KEYS = {
    Qt.Key.Key_Control,
    Qt.Key.Key_Shift,
    Qt.Key.Key_Alt,
    Qt.Key.Key_Meta,
    Qt.Key.Key_AltGr,
    Qt.Key.Key_CapsLock,
    Qt.Key.Key_NumLock,
}

_MOUSE_NAMES = {
    Qt.MouseButton.LeftButton: "click(left)",
    Qt.MouseButton.RightButton: "click(right)",
    Qt.MouseButton.MiddleButton: "click(middle)",
}


class _CaptureField(QPlainTextEdit):
    """Campo que registra os eventos de entrada em vez de editar texto."""

    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setPlaceholderText(tr("test_placeholder"))
        self.setUndoRedoEnabled(False)

    def _log(self, entry: str) -> None:
        self.appendPlainText(entry)

    def keyPressEvent(self, event) -> None:  # noqa: N802 (API Qt)
        if event.isAutoRepeat() or event.key() in _MODIFIER_KEYS:
            return
        text = QKeySequence(event.keyCombination()).toString(
            QKeySequence.SequenceFormat.NativeText
        )
        if text:
            self._log(text)

    def wheelEvent(self, event) -> None:  # noqa: N802 (API Qt)
        delta = event.angleDelta().y() or event.angleDelta().x()
        if delta:
            self._log("wheel ↑" if delta > 0 else "wheel ↓")

    def mousePressEvent(self, event) -> None:  # noqa: N802 (API Qt)
        super().mousePressEvent(event)  # mantém o foco por clique
        name = _MOUSE_NAMES.get(event.button())
        if name:
            self._log(name)

    def contextMenuEvent(self, event) -> None:  # noqa: N802 (API Qt)
        # Sem menu de contexto: o clique direito também é evento de teste.
        event.accept()


class TestArea(QGroupBox):
    def __init__(self) -> None:
        super().__init__(tr("group_test"))

        self._field = _CaptureField()

        hint = QLabel(tr("test_hint"))
        hint.setProperty("role", "dim")
        hint.setWordWrap(True)

        clear = QPushButton(tr("btn_clear_log"))
        clear.clicked.connect(self._field.clear)

        layout = QVBoxLayout(self)
        layout.addWidget(self._field)
        layout.addWidget(hint)
        layout.addWidget(clear, alignment=Qt.AlignmentFlag.AlignRight)
