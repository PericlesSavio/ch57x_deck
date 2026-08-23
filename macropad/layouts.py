# SPDX-License-Identifier: GPL-3.0-or-later
"""Layouts físicos de teclado (ABNT2, AZERTY, QWERTZ…) para o teclado visual.

O macropad grava a **posição física** da tecla (código HID, nome no dialeto do
firmware), nunca um caractere. Que caractere sai depende do layout ativo no
sistema operacional de quem usa o macropad. Este módulo só ajusta o **rótulo**
mostrado em cada botão do teclado visual, para que ele espelhe o teclado físico
do usuário — a tecla continua gravando o mesmo nome HID.

Cada layout é um dicionário `nome_HID (posição, igual ao US) -> rótulo`. Só as
posições que diferem do US aparecem; as demais mantêm o rótulo US de
`keyboard_widget._ROWS`. Rótulos com dois símbolos mostram "sem shift · com
shift"; "´", "~", "^", "¨", "`" indicam acentos que no layout são teclas
mortas.

Aviso: só o ABNT2 foi conferido com hardware/layout real; AZERTY, QWERTZ e os
demais seguem o mapeamento padrão de cada layout, mas não foram testados.
"""

from __future__ import annotations

DEFAULT_LAYOUT = "us"

# Ordem de exibição no menu.
LAYOUT_ORDER = ["us", "abnt2", "es", "fr", "de", "uk"]

# Rótulo (posição US -> símbolo no layout). Chave i18n do nome: "kbd_<id>".
KEYBOARD_LAYOUTS: dict[str, dict[str, str]] = {
    # US / Internacional — rótulos originais de _ROWS, nada a sobrepor.
    "us": {},
    # ABNT2 (Brasil) — QWERTY; muda pontuação e acrescenta Ç e acentos mortos.
    "abnt2": {
        "grave": "' \"",
        "leftbracket": "´ `",
        "rightbracket": "[ {",
        "backslash": "] }",
        "semicolon": "Ç",
        "quote": "~ ^",
        "slash": "; :",
    },
    # Espanhol (España) — QWERTY; Ñ, Ç e acentos mortos.
    "es": {
        "grave": "º ª",
        "minus": "' ?",
        "equal": "¡ ¿",
        "leftbracket": "` ^",
        "rightbracket": "+ *",
        "semicolon": "Ñ",
        "quote": "´ ¨",
        "backslash": "Ç",
        "slash": "- _",
    },
    # Francês (AZERTY) — reordena letras e a fileira de números.
    "fr": {
        "grave": "²",
        "1": "&",
        "2": "é",
        "3": "\"",
        "4": "'",
        "5": "(",
        "6": "-",
        "7": "è",
        "8": "_",
        "9": "ç",
        "0": "à",
        "minus": ")",
        "q": "A",
        "w": "Z",
        "a": "Q",
        "z": "W",
        "m": ",",
        "leftbracket": "^ ¨",
        "rightbracket": "$",
        "semicolon": "M",
        "quote": "ù",
        "backslash": "* µ",
        "comma": ";",
        "dot": ":",
        "slash": "!",
    },
    # Alemão (QWERTZ) — troca Y/Z e acrescenta Ä Ö Ü ß.
    "de": {
        "grave": "^ °",
        "2": "2 \"",
        "3": "3 §",
        "6": "6 &",
        "7": "7 /",
        "8": "8 (",
        "9": "9 )",
        "0": "0 =",
        "minus": "ß ?",
        "equal": "´ `",
        "y": "Z",
        "z": "Y",
        "leftbracket": "Ü",
        "rightbracket": "+ *",
        "semicolon": "Ö",
        "quote": "Ä",
        "backslash": "# '",
        "comma": ", ;",
        "dot": ". :",
        "slash": "- _",
    },
    # Reino Unido (UK) — QWERTY; £, símbolos de shift diferentes.
    "uk": {
        "2": "2 \"",
        "3": "3 £",
        "quote": "' @",
        "backslash": "# ~",
        "grave": "` ¬",
    },
}


def labels_for(layout_id: str) -> dict[str, str]:
    """Sobreposições de rótulo do layout (vazio para US ou id desconhecido)."""
    return KEYBOARD_LAYOUTS.get(layout_id, {})
