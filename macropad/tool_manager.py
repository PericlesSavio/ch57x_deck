# SPDX-License-Identifier: GPL-3.0-or-later
"""Diálogo de gerenciamento do ch57x-keyboard-tool.

Mostra a versão instalada, instala/atualiza para a versão estável verificada
(conferindo o SHA-256 antes de usar) e procura no GitHub se saiu uma estável
nova. Só instala binários cujo hash bate com o valor embutido — nunca um
download não verificado.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from .backend import Backend, LATEST_KNOWN
from .i18n import tr


def _version_tuple(tag: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in tag.lstrip("v").split("."))
    except ValueError:
        return ()


class ToolManagerDialog(QDialog):
    """Instala/atualiza o binário de gravação para a estável, sempre verificado."""

    def __init__(self, backend: Backend, parent=None) -> None:
        super().__init__(parent)
        self.backend = backend
        self.setWindowTitle(tr("tool_title"))
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)

        self._installed_label = QLabel()
        self._installed_label.setProperty("role", "heading")
        layout.addWidget(self._installed_label)

        stable = QLabel(tr("tool_stable", version=LATEST_KNOWN))
        layout.addWidget(stable)

        info = QLabel(tr("tool_info"))
        info.setProperty("role", "dim")
        info.setWordWrap(True)
        layout.addWidget(info)

        row = QHBoxLayout()
        self._install_btn = QPushButton(tr("tool_install", version=LATEST_KNOWN))
        self._install_btn.setProperty("role", "accent")
        self._install_btn.clicked.connect(self._install)
        row.addWidget(self._install_btn)
        self._check_btn = QPushButton(tr("tool_check_online"))
        self._check_btn.clicked.connect(self._check_online)
        row.addWidget(self._check_btn)
        row.addStretch()
        layout.addLayout(row)

        self._status = QLabel()
        self._status.setProperty("role", "dim")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

        close = QPushButton(tr("tool_close"))
        close.clicked.connect(self.accept)
        layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignRight)

        self._refresh_installed()

    # ------------------------------------------------------------------

    def _refresh_installed(self) -> None:
        version = self.backend.installed_version()
        self._installed_label.setText(
            tr("tool_installed", version=version)
            if version
            else tr("tool_not_installed")
        )

    def _set_busy(self, message: str) -> None:
        self._status.setText(message)
        self._install_btn.setEnabled(False)
        self._check_btn.setEnabled(False)
        QApplication.processEvents()  # o download é síncrono; ao menos pinta o texto

    def _set_idle(self) -> None:
        self._install_btn.setEnabled(True)
        self._check_btn.setEnabled(True)

    # ------------------------------------------------------------------

    def _install(self) -> None:
        self._set_busy(tr("tool_downloading", version=LATEST_KNOWN))
        try:
            self.backend.install_tool()  # LATEST_KNOWN, baixa + confere o SHA-256
        except RuntimeError as exc:
            self._status.setText(tr("tool_failed", msg=str(exc)))
        else:
            self._status.setText(tr("tool_ok", version=LATEST_KNOWN))
            self._refresh_installed()
        finally:
            self._set_idle()

    def _check_online(self) -> None:
        self._set_busy(tr("tool_checking"))
        latest = self.backend.latest_online()
        self._set_idle()
        if not latest:
            self._status.setText(tr("tool_offline"))
            return

        installed = self.backend.installed_version()
        if _version_tuple(latest) > _version_tuple(LATEST_KNOWN):
            # Saiu uma estável mais nova do que a que o app sabe verificar.
            self._status.setText(tr("tool_app_outdated", version=latest))
        elif installed == LATEST_KNOWN:
            self._status.setText(tr("tool_uptodate", version=LATEST_KNOWN))
        else:
            self._status.setText(tr("tool_available_known", version=LATEST_KNOWN))
