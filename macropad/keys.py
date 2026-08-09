"""Catálogo das teclas, modificadores e ações aceitas pelo firmware CH57x.

A lista espelha a saída de `ch57x-keyboard-tool show-keys` (v1.7.0). Ela é usada
para montar os seletores da interface e para validar uma ação antes de gastar
uma chamada ao binário externo.
"""

from __future__ import annotations

import re

MODIFIERS = [
    "ctrl",
    "shift",
    "alt",
    "win",
    "rctrl",
    "rshift",
    "ralt",
    "rwin",
]

# Apelidos aceitos pelo firmware, mantidos para leitura de arquivos externos.
MODIFIER_ALIASES = {
    "opt": "alt",
    "cmd": "win",
    "ropt": "ralt",
    "rcmd": "rwin",
}

LETTERS = [chr(c) for c in range(ord("a"), ord("z") + 1)]
DIGITS = [str(d) for d in range(1, 10)] + ["0"]

PUNCTUATION = [
    "enter",
    "escape",
    "backspace",
    "tab",
    "space",
    "minus",
    "equal",
    "leftbracket",
    "rightbracket",
    "backslash",
    "nonushash",
    "semicolon",
    "quote",
    "grave",
    "comma",
    "dot",
    "slash",
    "capslock",
]

FUNCTION_KEYS = [f"f{n}" for n in range(1, 25)]

NAVIGATION = [
    "printscreen",
    "insert",
    "home",
    "pageup",
    "delete",
    "end",
    "pagedown",
    "right",
    "left",
    "down",
    "up",
]

NUMPAD = [
    "numlock",
    "numpadslash",
    "numpadasterisk",
    "numpadminus",
    "numpadplus",
    "numpadenter",
    "numpad1",
    "numpad2",
    "numpad3",
    "numpad4",
    "numpad5",
    "numpad6",
    "numpad7",
    "numpad8",
    "numpad9",
    "numpad0",
    "numpaddot",
    "numpadequal",
]

MISC = [
    "nonusbackslash",
    "application",
    "power",
    "macbrightnessdown",
    "macbrightnessup",
]

# Teclas de mídia não podem ser combinadas com modificadores nem encadeadas.
MEDIA_KEYS = [
    "next",
    "previous",
    "stop",
    "play",
    "mute",
    "volumeup",
    "volumedown",
    "favorites",
    "calculator",
    "screenlock",
]

MEDIA_ALIASES = {"prev": "previous"}

MOUSE_BUTTONS = ["left", "right", "middle"]

# Grupos exibidos no seletor da interface, na ordem em que aparecem.
# O primeiro elemento é a chave de tradução (ver i18n.STRINGS).
KEY_GROUPS: list[tuple[str, list[str]]] = [
    ("group.letters", LETTERS),
    ("group.digits", DIGITS),
    ("group.function", FUNCTION_KEYS),
    ("group.navigation", NAVIGATION),
    ("group.punct", PUNCTUATION),
    ("group.numpad", NUMPAD),
    ("group.misc", MISC),
]

ALL_KEYS: list[str] = [
    key for _group, keys in KEY_GROUPS for key in keys
]

_CUSTOM_CODE = re.compile(r"^<(\d{1,3})>$")
_MOUSE_ACTION = re.compile(r"^(wheel|click|move|drag)\(")


def normalize_modifier(name: str) -> str:
    """Converte apelidos (`opt`, `cmd`) na forma canônica."""
    name = name.strip().lower()
    return MODIFIER_ALIASES.get(name, name)


def normalize_media(name: str) -> str:
    name = name.strip().lower()
    return MEDIA_ALIASES.get(name, name)


def is_media(name: str) -> bool:
    return normalize_media(name) in MEDIA_KEYS


def is_mouse(expression: str) -> bool:
    return bool(_MOUSE_ACTION.match(expression.strip()))


def is_custom_code(expression: str) -> bool:
    match = _CUSTOM_CODE.match(expression.strip())
    return bool(match) and 0 <= int(match.group(1)) <= 255


def is_known_key(name: str) -> bool:
    return name.strip().lower() in ALL_KEYS
