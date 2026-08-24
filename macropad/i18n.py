# SPDX-License-Identifier: GPL-3.0-or-later
"""Internacionalização: pt-BR (padrão), inglês e espanhol.

As traduções ficam em macropad/locales/<código>.yaml (uma por idioma), fáceis
de editar por qualquer pessoa — para um idioma novo, copie en.yaml, traduza os
valores e registre o código em LANGUAGES. A língua escolhida fica persistida em
~/.config/ch57x_deck/settings.json; sem escolha salva, segue o locale do
sistema.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

from .backend import config_dir

DEFAULT = "pt_BR"

LANGUAGES = {
    "pt_BR": "Português (Brasil)",
    "en": "English",
    "es": "Español",
}

_SETTINGS_FILE = "settings.json"

_LOCALES_DIR = Path(__file__).resolve().parent / "locales"


def _load_strings() -> dict[str, dict[str, str]]:
    """Carrega macropad/locales/<código>.yaml em {chave: {idioma: texto}}."""
    strings: dict[str, dict[str, str]] = {}
    for lang in LANGUAGES:
        path = _LOCALES_DIR / f"{lang}.yaml"
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except OSError:
            data = {}
        for key, text in data.items():
            strings.setdefault(key, {})[lang] = text
    return strings


STRINGS: dict[str, dict[str, str]] = _load_strings()


def _settings_path():
    return config_dir() / _SETTINGS_FILE


def _detect_system_language() -> str:
    lang = (
        os.environ.get("LC_ALL")
        or os.environ.get("LC_MESSAGES")
        or os.environ.get("LANG")
        or ""
    ).lower()
    if lang.startswith("pt"):
        return "pt_BR"
    if lang.startswith("es"):
        return "es"
    return "en"


def _load_language() -> str:
    try:
        data = json.loads(_settings_path().read_text())
        saved = data.get("language")
        if saved in LANGUAGES:
            return saved
    except (OSError, ValueError):
        pass
    return _detect_system_language()


_current = _load_language()


def current_language() -> str:
    return _current


def set_language(code: str) -> None:
    """Troca a língua ativa e persiste a escolha."""
    global _current
    if code not in LANGUAGES:
        raise ValueError(f"Língua desconhecida: {code!r}")
    _current = code

    path = _settings_path()
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        data = {}
    data["language"] = code
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def tr(key: str, **fmt) -> str:
    """Devolve a string na língua ativa, com fallback pt-BR → chave."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(_current) or entry.get(DEFAULT) or key
    return text.format(**fmt) if fmt else text


# Mantém as instâncias vivas (o Qt as coleta se perder a referência).
_qt_translators: list = []


def install_qt_translations(app) -> None:
    """Traduz os textos padrão do Qt (Mostrar/Ocultar detalhes, OK, Cancelar…)
    para a língua ativa, se houver o .qm correspondente no PySide6.

    Chamado na inicialização e a cada troca de idioma. Sem efeito no inglês
    (padrão do Qt) ou se o arquivo de tradução não existir."""
    from PySide6.QtCore import QLibraryInfo, QTranslator

    for old in _qt_translators:
        app.removeTranslator(old)
    _qt_translators.clear()

    if _current == "en":
        return
    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator()
    if translator.load(f"qtbase_{_current}", path):
        app.installTranslator(translator)
        _qt_translators.append(translator)
