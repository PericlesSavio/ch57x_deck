# SPDX-License-Identifier: GPL-3.0-or-later
"""Testes do backend que não tocam a rede (releases pinados e recusas)."""

from __future__ import annotations

import re

import pytest

from macropad import backend


def test_latest_known_is_registered():
    assert backend.LATEST_KNOWN in backend.KNOWN_RELEASES


def test_pinned_hashes_are_valid_sha256():
    for version, targets in backend.KNOWN_RELEASES.items():
        assert targets, f"{version} sem alvos"
        for target, digest in targets.items():
            assert re.fullmatch(r"[0-9a-f]{64}", digest), f"{version}/{target}"


def test_known_versions_sorted_newest_first():
    b = backend.Backend()
    versions = b.known_versions()
    if not versions:  # arquitetura sem release pronta
        pytest.skip("sem alvo para esta arquitetura")
    assert versions[0] == max(
        versions, key=lambda t: tuple(int(p) for p in t.lstrip("v").split("."))
    )


def test_download_url_uses_version_and_target():
    b = backend.Backend()
    if b.target() is None:
        pytest.skip("sem alvo para esta arquitetura")
    url = b.download_url("v1.7.0")
    assert "v1.7.0" in url and url.endswith(".tar.gz")
    assert backend.TOOL_REPO in url


def test_install_tool_refuses_unpinned_version(monkeypatch):
    """Uma versão sem hash embutido é recusada antes de qualquer download."""
    b = backend.Backend()

    def _boom(*a, **k):
        raise AssertionError("não deveria baixar uma versão não verificada")

    monkeypatch.setattr(b, "fetch_release", _boom)
    with pytest.raises(RuntimeError, match="hash verificado"):
        b.install_tool("v0.0.0")


def test_pinned_sha256_unknown_is_none():
    assert backend.Backend().pinned_sha256("v0.0.0") is None
