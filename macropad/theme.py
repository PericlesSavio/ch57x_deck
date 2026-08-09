"""Tema visual: paletas escura (Monokai) e clara, cantos retos em ambas.

Cor viva só em detalhes pontuais (destaques, botões de risco/envio); o
restante fica na escala de cinzas de cada paleta.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    BG: str
    BG_ALT: str
    BG_RAISED: str
    BG_HOVER: str
    BORDER: str
    TEXT: str
    TEXT_DIM: str
    ACCENT: str
    ACCENT_DIM: str
    WARN: str
    DANGER: str
    DANGER_DIM: str
    SELECTED: str


DARK = Palette(
    BG="#272822",          # fundo geral
    BG_ALT="#1e1f1c",      # painéis rebaixados
    BG_RAISED="#32332c",   # cartões e botões
    BG_HOVER="#3e3f38",
    BORDER="#4a4b44",
    TEXT="#d6d6d1",
    TEXT_DIM="#8f908a",
    ACCENT="#c2c3bd",      # cinza claro — destaque neutro
    ACCENT_DIM="#7a7b75",
    WARN="#fd971f",        # laranja Monokai — avisos pontuais
    DANGER="#c25c5c",      # vermelho escuro Monokai — ações de risco/instalação
    DANGER_DIM="#7a3a3a",
    SELECTED="#49483e",
)

LIGHT = Palette(
    BG="#f2f2ee",          # fundo geral
    BG_ALT="#e6e6df",      # painéis rebaixados (afundados)
    BG_RAISED="#ffffff",   # cartões e botões (elevados)
    BG_HOVER="#eaeae4",
    BORDER="#cccec5",
    TEXT="#272822",        # mesmo tom do fundo escuro do tema dark
    TEXT_DIM="#797a73",
    ACCENT="#43443b",      # cinza escuro — destaque neutro
    ACCENT_DIM="#8a8b83",
    WARN="#b35900",        # laranja escurecido — contraste em fundo claro
    DANGER="#a13a3a",      # vermelho escurecido — idem
    DANGER_DIM="#d9b3b3",
    SELECTED="#dcdcd2",
)

PALETTES: dict[str, Palette] = {"dark": DARK, "light": LIGHT}
DEFAULT_THEME = "dark"


def build_stylesheet(palette: Palette) -> str:
    BG = palette.BG
    BG_ALT = palette.BG_ALT
    BG_RAISED = palette.BG_RAISED
    BG_HOVER = palette.BG_HOVER
    BORDER = palette.BORDER
    TEXT = palette.TEXT
    TEXT_DIM = palette.TEXT_DIM
    ACCENT = palette.ACCENT
    ACCENT_DIM = palette.ACCENT_DIM
    WARN = palette.WARN  # noqa: F841 (mantido para simetria com os outros temas)
    DANGER = palette.DANGER
    DANGER_DIM = palette.DANGER_DIM
    SELECTED = palette.SELECTED

    return f"""
* {{
    border-radius: 0;
}}

QWidget {{
    background: {BG};
    color: {TEXT};
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background: {BG};
}}

QLabel {{
    background: transparent;
}}

QLabel[role="dim"] {{
    color: {TEXT_DIM};
}}

QLabel[role="heading"] {{
    color: {TEXT};
    font-size: 14px;
    font-weight: bold;
}}

QPushButton {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
    padding: 6px 14px;
}}

QPushButton:hover {{
    background: {BG_HOVER};
}}

QPushButton:pressed {{
    background: {SELECTED};
}}

QPushButton:disabled {{
    color: {TEXT_DIM};
    background: {BG_ALT};
}}

QPushButton[role="accent"] {{
    border: 1px solid {ACCENT_DIM};
    color: {ACCENT};
    font-weight: bold;
}}

QPushButton[role="accent"]:hover {{
    background: {BG_HOVER};
    border-color: {ACCENT};
}}

QPushButton[role="danger"] {{
    border: 1px solid {DANGER_DIM};
    color: {DANGER};
    font-weight: bold;
}}

QPushButton[role="danger"]:hover {{
    background: {BG_HOVER};
    border-color: {DANGER};
}}

/* Botões da grade do macropad */
QPushButton[role="pad"] {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
    min-width: 96px;
    min-height: 72px;
    font-family: monospace;
}}

QPushButton[role="pad"]:checked {{
    background: {SELECTED};
    border: 1px solid {ACCENT};
}}

QPushButton[role="knob"] {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
    min-width: 72px;
    min-height: 72px;
    font-family: monospace;
}}

QPushButton[role="knob"]:checked {{
    background: {SELECTED};
    border: 1px solid {ACCENT};
}}

/* Teclas do teclado visual */
QPushButton[role="kb"] {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
    padding: 1px 2px;
    min-width: 0;
    font-size: 10px;
    font-family: monospace;
    color: {TEXT_DIM};
}}

QPushButton[role="kb"]:hover {{
    background: {BG_HOVER};
    color: {TEXT};
}}

QPushButton[role="kb"]:checked {{
    background: {SELECTED};
    border: 1px solid {ACCENT};
    color: {TEXT};
}}

QComboBox, QLineEdit, QSpinBox {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    padding: 4px 8px;
    selection-background-color: {SELECTED};
    selection-color: {TEXT};
}}

QComboBox:focus, QLineEdit:focus, QSpinBox:focus {{
    border: 1px solid {TEXT_DIM};
}}

QComboBox::drop-down {{
    border: none;
    width: 22px;
}}

QComboBox QAbstractItemView {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    selection-background-color: {SELECTED};
    selection-color: {TEXT};
    outline: none;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    top: -1px;
}}

QTabBar::tab {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    padding: 6px 18px;
    margin-right: -1px;
    color: {TEXT_DIM};
}}

/* O margin-right negativo (que funde as bordas internas) não pode vazar
   na última aba, senão a borda direita dela é cortada. */
QTabBar::tab:last {{
    margin-right: 0;
}}

QTabBar::tab:selected {{
    background: {BG};
    color: {TEXT};
    border-bottom: 1px solid {BG};
}}

QTabBar::tab:hover {{
    color: {TEXT};
}}

QGroupBox {{
    border: 1px solid {BORDER};
    margin-top: 10px;
    padding-top: 8px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: {TEXT_DIM};
}}

QStatusBar {{
    background: {BG_ALT};
    border-top: 1px solid {BORDER};
    color: {TEXT_DIM};
}}

QPlainTextEdit, QTextEdit, QListWidget {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    font-family: monospace;
    selection-background-color: {SELECTED};
    selection-color: {TEXT};
}}

QListWidget::item:selected {{
    background: {SELECTED};
    color: {TEXT};
}}

QScrollBar:vertical {{
    background: {BG_ALT};
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background: {BG_HOVER};
    min-height: 24px;
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
}}

QToolTip {{
    background: {BG_ALT};
    color: {TEXT};
    border: 1px solid {BORDER};
}}

QMessageBox {{
    background: {BG};
}}

/* Overlay modal: escurece tudo atrás do card de instalação. */
QWidget#installOverlay {{
    background: rgba(0, 0, 0, 160);
}}

QFrame#installCard {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
}}

QLabel[role="dangerIcon"] {{
    color: {DANGER};
    font-size: 28px;
}}
"""


def stylesheet_for(mode: str) -> str:
    return build_stylesheet(PALETTES.get(mode, DARK))


# Compatibilidade: quem só quer o tema padrão (escuro) continua funcionando.
STYLESHEET = build_stylesheet(DARK)
