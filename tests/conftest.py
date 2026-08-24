# SPDX-License-Identifier: GPL-3.0-or-later
"""Configuração comum dos testes: Qt sem display e config/dados isolados."""

import os
import tempfile

# Roda o Qt sem servidor gráfico.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Isola leitura/escrita de config e dados do ~/.config real do usuário.
_tmp = tempfile.mkdtemp(prefix="ch57x_deck_tests_")
os.environ.setdefault("XDG_CONFIG_HOME", os.path.join(_tmp, "config"))
os.environ.setdefault("XDG_DATA_HOME", os.path.join(_tmp, "data"))
