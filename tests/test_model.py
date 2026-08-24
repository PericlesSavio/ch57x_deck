# SPDX-License-Identifier: GPL-3.0-or-later
"""Testes do modelo de dados e da (de)serialização YAML."""

from __future__ import annotations

import pytest

from macropad import model


def test_default_config_is_12_keys_2_knobs():
    config = model.default_config()
    assert (config.rows, config.columns, config.knob_count) == (3, 4, 2)
    assert config.button_count == 12
    assert len(config.layers) == model.LAYER_COUNT


def test_default_config_seeds_f13_to_f24_on_first_layer():
    config = model.default_config()
    actions = [
        config.get(0, r, c)
        for r in range(config.rows)
        for c in range(config.columns)
    ]
    assert actions == [f"f{n}" for n in range(13, 25)]
    # Camadas seguintes começam vazias.
    assert all(config.get(1, r, c) == "" for r in range(3) for c in range(4))


def test_button_label_counts_left_to_right():
    config = model.Config(rows=3, columns=4)
    assert config.button_label(0, 0) == "K1"
    assert config.button_label(0, 3) == "K4"
    assert config.button_label(2, 3) == "K12"


def test_yaml_roundtrip_preserves_actions():
    config = model.default_config()
    config.set(0, 0, 0, "ctrl-c,ctrl-v")
    config.layers[0].knobs[0].ccw = "volumedown"
    restored = model.Config.from_yaml(config.to_yaml())
    assert restored.to_yaml_dict() == config.to_yaml_dict()
    assert restored.get(0, 0, 0) == "ctrl-c,ctrl-v"
    assert restored.layers[0].knobs[0].ccw == "volumedown"


def test_empty_action_serializes_as_null():
    config = model.Config(rows=1, columns=2, knob_count=0)
    config.set(0, 0, 0, "a")  # mantém a camada viva (senão seria podada)
    dumped = config.to_yaml_dict()
    assert dumped["layers"][0]["buttons"] == [["a", None]]


def test_fully_empty_config_prunes_all_layers():
    config = model.Config(rows=1, columns=1, knob_count=0)
    assert config.to_yaml_dict()["layers"] == []


def test_trailing_empty_layers_are_pruned():
    config = model.default_config()  # só a camada 1 tem ações
    dumped = config.to_yaml_dict()
    assert len(dumped["layers"]) == 1


def test_disable_empty_sends_zero_code_and_keeps_all_layers():
    config = model.default_config()  # camada 1 = F13–F24, camadas 2/3 vazias
    config.set(0, 0, 0, "")  # limpa K1
    dumped = config.to_yaml_dict(disable_empty=True)
    # tecla vazia vira <0> (o upload grava e desativa, em vez de pular null)
    assert dumped["layers"][0]["buttons"][0][0] == "<0>"
    # nenhuma camada omitida — todas gravadas
    assert len(dumped["layers"]) == model.LAYER_COUNT
    assert dumped["layers"][1]["buttons"][0][0] == "<0>"


def test_default_mode_still_uses_null():
    config = model.Config(rows=1, columns=2, knob_count=0)
    config.set(0, 0, 0, "a")
    assert config.to_yaml_dict()["layers"][0]["buttons"][0] == ["a", None]


def test_resize_preserves_existing_cells():
    config = model.Config(rows=3, columns=4, knob_count=2)
    config.set(0, 0, 0, "a")
    config.set(0, 2, 3, "b")
    config.rows, config.columns = 3, 5  # cresce uma coluna
    config.normalize()
    assert config.get(0, 0, 0) == "a"
    assert config.get(0, 2, 3) == "b"
    assert config.get(0, 0, 4) == ""  # coluna nova vem vazia


def test_shrink_drops_out_of_range_cells():
    config = model.Config(rows=3, columns=4)
    config.set(0, 2, 3, "x")
    config.rows, config.columns = 1, 3
    config.normalize()
    assert len(config.layers[0].buttons) == 1
    assert all(len(row) == 3 for row in config.layers[0].buttons)


@pytest.mark.parametrize(
    "text",
    [
        "rows: 0\ncolumns: 4\nknobs: 2",
        "rows: 3\ncolumns: 4\nknobs: -1",
        "orientation: diagonal",
        "rows: abc",
    ],
)
def test_from_yaml_rejects_invalid_configs(text):
    with pytest.raises(model.ConfigError):
        model.Config.from_yaml(text)


def test_from_yaml_rejects_non_mapping():
    with pytest.raises(model.ConfigError):
        model.Config.from_yaml("- just\n- a\n- list")


def test_is_macro():
    assert model.is_macro("ctrl-c,ctrl-v")
    assert not model.is_macro("ctrl-c")
    assert not model.is_macro("")


def test_variants_key_count_matches_grid():
    for variant in model.VARIANTS:
        assert variant.keys == variant.rows * variant.columns


def test_exactly_one_tested_variant_is_12_2():
    tested = [v for v in model.VARIANTS if v.tested]
    assert len(tested) == 1
    assert (tested[0].keys, tested[0].knobs) == (12, 2)
