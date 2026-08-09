"""Ponto de entrada: python -m macropad"""

import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from . import settings, theme
from .main_window import MainWindow

# assets/ é irmã do pacote (não fica dentro de macropad/), então o caminho é
# relativo à localização deste arquivo — funciona tanto rodando via
# `python run.py` quanto via `pip install -e .` (o -e mantém o link para o
# repositório, então o arquivo continua no mesmo lugar).
_ICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "ch57x-deck.svg"

_DESKTOP_ID = "ch57x-deck"


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
    if _ICON_PATH.is_file():
        app.setWindowIcon(QIcon(str(_ICON_PATH)))
    app.setStyle("Fusion")  # base neutra e idêntica em qualquer distro/desktop
    theme_mode = settings.get("theme", theme.DEFAULT_THEME)
    app.setStyleSheet(theme.stylesheet_for(theme_mode))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
