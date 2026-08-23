# SPDX-License-Identifier: GPL-3.0-or-later
"""Ponto de entrada: python -m macropad"""

import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from . import settings, theme
from .main_window import MainWindow

_DESKTOP_ID = "ch57x-deck"


def _icon_path() -> Path | None:
    """Primeiro SVG do ícone que existir, cobrindo cada forma de instalação.

    - repositório / `pip install -e .`: assets/ ao lado do pacote;
    - `pip install --user .` + install.sh: hicolor no ~/.local/share;
    - pacote da distro: hicolor em /usr/share.
    (Sem `-e`, assets/ não é copiado para site-packages, daí a busca no
    diretório de ícones onde o install.sh deposita o SVG.)
    """
    candidates = [
        Path(__file__).resolve().parent.parent / "assets" / f"{_DESKTOP_ID}.svg",
    ]
    xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    xdg_data_dirs = os.environ.get(
        "XDG_DATA_DIRS", "/usr/local/share:/usr/share"
    ).split(":")
    for base in [xdg_data_home, *xdg_data_dirs]:
        candidates.append(
            Path(base) / "icons" / "hicolor" / "scalable" / "apps" / f"{_DESKTOP_ID}.svg"
        )
    return next((p for p in candidates if p.is_file()), None)


def _desktop_file_installed() -> bool:
    """True se assets/ch57x-deck.desktop já foi copiado para um diretório
    XDG de aplicativos (ver README, seção "Ícone e atalho..."). Só então faz
    sentido anunciar o desktop-file-id: sem o arquivo instalado, o
    xdg-desktop-portal não acha o que registrar e emite um aviso no console
    (inofensivo, mas evitável)."""
    xdg_data_home = os.environ.get(
        "XDG_DATA_HOME", os.path.expanduser("~/.local/share")
    )
    xdg_data_dirs = os.environ.get(
        "XDG_DATA_DIRS", "/usr/local/share:/usr/share"
    ).split(":")
    for base in [xdg_data_home, *xdg_data_dirs]:
        if (Path(base) / "applications" / f"{_DESKTOP_ID}.desktop").is_file():
            return True
    return False


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(_DESKTOP_ID)
    # Casa com o id de assets/ch57x-deck.desktop — é assim que KDE/GNOME
    # (sobretudo no Wayland) associam a janela em execução ao ícone instalado.
    # Só declarado quando o .desktop está de fato instalado (ver função acima).
    if _desktop_file_installed():
        app.setDesktopFileName(_DESKTOP_ID)
    icon = _icon_path()
    if icon is not None:
        app.setWindowIcon(QIcon(str(icon)))
    elif QIcon.hasThemeIcon(_DESKTOP_ID):
        app.setWindowIcon(QIcon.fromTheme(_DESKTOP_ID))
    app.setStyle("Fusion")  # base neutra e idêntica em qualquer distro/desktop
    app.setStyleSheet(theme.stylesheet_for(settings.get("theme", theme.DEFAULT_SETTING)))

    # No modo "sistema", reaplica o estilo quando o SO alterna claro/escuro.
    def _reapply_on_scheme_change(*_) -> None:
        stored = settings.get("theme", theme.DEFAULT_SETTING)
        if stored == theme.THEME_SYSTEM:
            app.setStyleSheet(theme.stylesheet_for(stored))

    try:
        app.styleHints().colorSchemeChanged.connect(_reapply_on_scheme_change)
    except AttributeError:
        pass  # Qt < 6.5: sem sinal de troca; o tema fixo ainda funciona

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
