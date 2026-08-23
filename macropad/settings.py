# SPDX-License-Identifier: GPL-3.0-or-later
"""Preferências persistentes do app (~/.config/ch57x_deck/settings.json).

O mesmo arquivo guarda a língua escolhida (ver i18n.py) e as opções de
interface, como a visibilidade da área de teste.
"""

from __future__ import annotations

import json

from .backend import config_dir

_FILE = "settings.json"


def _path():
    return config_dir() / _FILE


def load() -> dict:
    try:
        data = json.loads(_path().read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def get(key: str, default=None):
    return load().get(key, default)


def save(key: str, value) -> None:
    data = load()
    data[key] = value
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
