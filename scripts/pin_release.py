#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Atualiza os SHA-256 pinados do ch57x-keyboard-tool em macropad/backend.py.

Ferramenta de MANUTENÇÃO, rodada à mão pelo mantenedor quando quiser adotar uma
nova versão estável — nunca roda no app do usuário final. Baixa os .tar.gz de
cada alvo Linux, calcula o hash e reescreve `KNOWN_RELEASES` + `LATEST_KNOWN`.

Uso:
    python scripts/pin_release.py            # última estável do GitHub
    python scripts/pin_release.py v1.7.1     # uma tag específica

Depois: revise com `git diff`, rode `pytest` e commite.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from macropad.backend import TOOL_NAME, TOOL_REPO, _RELEASE_TARGETS  # noqa: E402

BACKEND = ROOT / "macropad" / "backend.py"


def latest_stable() -> str:
    """Tag da última release estável (não prerelease) no GitHub."""
    url = f"https://api.github.com/repos/{TOOL_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": TOOL_NAME},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)["tag_name"]


def sha256_of_url(url: str) -> str:
    digest = hashlib.sha256()
    with urllib.request.urlopen(url, timeout=120) as resp:
        for chunk in iter(lambda: resp.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_hashes(version: str) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for target in _RELEASE_TARGETS.values():
        url = (
            f"https://github.com/{TOOL_REPO}/releases/download/"
            f"{version}/{TOOL_NAME}-{target}.tar.gz"
        )
        print(f"  baixando {target}…", end=" ", flush=True)
        try:
            digest = sha256_of_url(url)
        except OSError as exc:
            print(f"pulado ({exc})")
            continue
        print(f"sha256 = {digest}")
        hashes[target] = digest
    return hashes


def render_block(version: str, hashes: dict[str, str]) -> str:
    lines = [
        "KNOWN_RELEASES: dict[str, dict[str, str]] = {",
        f'    "{version}": {{',
    ]
    for target, digest in hashes.items():
        lines.append(f'        "{target}": "{digest}",')
    lines += ["    },", "}", ""]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    version = argv[1] if len(argv) > 1 else latest_stable()
    if not version.startswith("v"):
        version = "v" + version

    print(f"Pinando {TOOL_NAME} {version}")
    hashes = collect_hashes(version)
    if not hashes:
        print("Nenhum artefato baixado — nada a fazer.", file=sys.stderr)
        return 1

    text = BACKEND.read_text(encoding="utf-8")
    new_block = render_block(version, hashes)

    text, replaced = re.subn(
        r"KNOWN_RELEASES: dict\[str, dict\[str, str\]\] = \{.*?\n\}\n",
        lambda _m: new_block,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if replaced != 1:
        print("Não achei o bloco KNOWN_RELEASES em backend.py.", file=sys.stderr)
        return 2

    text, replaced = re.subn(
        r'LATEST_KNOWN = "[^"]*"',
        lambda _m: f'LATEST_KNOWN = "{version}"',
        text,
        count=1,
    )
    if replaced != 1:
        print("Não achei LATEST_KNOWN em backend.py.", file=sys.stderr)
        return 2

    BACKEND.write_text(text, encoding="utf-8")
    print(f"\n{BACKEND.relative_to(ROOT)} atualizado: LATEST_KNOWN = {version}")
    print("Revise com `git diff`, rode `pytest` e commite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
