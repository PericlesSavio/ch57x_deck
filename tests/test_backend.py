# SPDX-License-Identifier: GPL-3.0-or-later
"""Testes do backend que não tocam a rede."""

from __future__ import annotations

import pytest

from macropad import backend


def test_default_version_looks_like_a_tag():
    assert backend.DEFAULT_VERSION.startswith("v")


def test_download_url_uses_version_and_target():
    b = backend.Backend()
    if b.target() is None:
        pytest.skip("sem alvo de release para esta arquitetura")
    url = b.download_url("v1.7.0")
    assert "v1.7.0" in url and url.endswith(".tar.gz")
    assert backend.TOOL_REPO in url


def test_download_url_defaults_to_default_version():
    b = backend.Backend()
    if b.target() is None:
        pytest.skip("sem alvo de release para esta arquitetura")
    assert backend.DEFAULT_VERSION in b.download_url()


def test_download_url_none_when_arch_unsupported(monkeypatch):
    b = backend.Backend()
    monkeypatch.setattr(b, "target", lambda: None)
    assert b.download_url("v1.7.0") is None
