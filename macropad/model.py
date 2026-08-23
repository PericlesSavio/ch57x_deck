# SPDX-License-Identifier: GPL-3.0-or-later
"""Modelo de dados da configuração do macropad.

Uma ação é guardada como string no mesmo dialeto que o firmware entende
(`ctrl-c`, `alt-f4`, `ctrl-c,ctrl-v`, `<110>`, `click(left)`, `play`), o que
mantém ida e volta fiel ao YAML sem perder nada que a interface ainda não saiba
editar.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import yaml

from . import keys as keycat

ORIENTATIONS = ["normal", "upsidedown", "clockwise", "counterclockwise"]

ORIENTATION_LABELS = {
    "normal": "Normal — teclas à esquerda, knobs à direita",
    "upsidedown": "De cabeça para baixo — teclas à direita, knobs à esquerda",
    "clockwise": "Horário — teclas em cima, knobs embaixo",
    "counterclockwise": "Anti-horário — teclas embaixo, knobs em cima",
}

LAYER_COUNT = 3


@dataclass(frozen=True)
class Variant:
    """Um modelo de macropad CH57x, em teclas × knobs.

    As dimensões `rows`/`columns` são o arranjo físico presumido de cada
    modelo genérico; só a variante de 12 teclas + 2 knobs foi testada com
    hardware real (`tested=True`). Se um preset não bater com o seu
    dispositivo, o layout pode ser ajustado à mão em "Personalizado…".
    """

    keys: int
    rows: int
    columns: int
    knobs: int
    tested: bool = False


# Modelos genéricos mais comuns do chip CH57x (3/6/9/12/15 teclas com knobs).
VARIANTS = [
    Variant(keys=3, rows=1, columns=3, knobs=1),
    Variant(keys=6, rows=2, columns=3, knobs=1),
    Variant(keys=9, rows=3, columns=3, knobs=1),
    Variant(keys=12, rows=3, columns=4, knobs=2, tested=True),
    Variant(keys=15, rows=3, columns=5, knobs=2),
]


class ConfigError(ValueError):
    """Configuração inconsistente com o layout declarado."""


@dataclass
class Knob:
    ccw: str = ""
    press: str = ""
    cw: str = ""

    def to_yaml(self) -> dict[str, str]:
        return {"ccw": self.ccw, "press": self.press, "cw": self.cw}

    @classmethod
    def from_yaml(cls, data: dict | None) -> "Knob":
        data = data or {}
        return cls(
            ccw=str(data.get("ccw") or ""),
            press=str(data.get("press") or ""),
            cw=str(data.get("cw") or ""),
        )


@dataclass
class Layer:
    """Uma camada: a grade de botões mais as ações dos knobs."""

    buttons: list[list[str]] = field(default_factory=list)
    knobs: list[Knob] = field(default_factory=list)

    def resize(self, rows: int, columns: int, knob_count: int) -> None:
        """Ajusta a camada ao layout, preservando o que já estava preenchido."""
        grid: list[list[str]] = []
        for r in range(rows):
            old = self.buttons[r] if r < len(self.buttons) else []
            grid.append([old[c] if c < len(old) else "" for c in range(columns)])
        self.buttons = grid

        knobs = list(self.knobs[:knob_count])
        while len(knobs) < knob_count:
            knobs.append(Knob())
        self.knobs = knobs


@dataclass
class Config:
    orientation: str = "normal"
    rows: int = 3
    columns: int = 4
    knob_count: int = 2
    layers: list[Layer] = field(default_factory=list)

    def __post_init__(self) -> None:
        while len(self.layers) < LAYER_COUNT:
            self.layers.append(Layer())
        self.layers = self.layers[:LAYER_COUNT]
        self.normalize()

    def normalize(self) -> None:
        """Garante que toda camada bate com o layout declarado."""
        for layer in self.layers:
            layer.resize(self.rows, self.columns, self.knob_count)

    @property
    def button_count(self) -> int:
        return self.rows * self.columns

    def button_label(self, row: int, column: int) -> str:
        """Rótulo estável de um botão, contando da esquerda para a direita."""
        return f"K{row * self.columns + column + 1}"

    def get(self, layer: int, row: int, column: int) -> str:
        return self.layers[layer].buttons[row][column]

    def set(self, layer: int, row: int, column: int, action: str) -> None:
        self.layers[layer].buttons[row][column] = action

    def copy(self) -> "Config":
        return Config(
            orientation=self.orientation,
            rows=self.rows,
            columns=self.columns,
            knob_count=self.knob_count,
            layers=[
                Layer(
                    buttons=[list(row) for row in layer.buttons],
                    knobs=[replace(k) for k in layer.knobs],
                )
                for layer in self.layers
            ],
        )

    # ------------------------------------------------------------------
    # YAML
    # ------------------------------------------------------------------

    def to_yaml_dict(self) -> dict:
        self.normalize()

        def cell(action: str) -> str | None:
            # O firmware não aceita string vazia; "sem ação" é null.
            return action if action.strip() else None

        layers = []
        for layer in self.layers:
            entry: dict = {
                "buttons": [[cell(a) for a in row] for row in layer.buttons]
            }
            if self.knob_count:
                entry["knobs"] = [
                    {slot: cell(v) for slot, v in k.to_yaml().items()}
                    for k in layer.knobs
                ]
            layers.append(entry)

        # Camadas vazias no fim da lista podem ser omitidas (o firmware
        # aceita menos camadas do que o teclado tem).
        def is_empty(entry: dict) -> bool:
            buttons_empty = all(a is None for row in entry["buttons"] for a in row)
            knobs_empty = all(
                v is None for k in entry.get("knobs", []) for v in k.values()
            )
            return buttons_empty and knobs_empty

        while layers and is_empty(layers[-1]):
            layers.pop()

        return {
            "orientation": self.orientation,
            "rows": self.rows,
            "columns": self.columns,
            "knobs": self.knob_count,
            "layers": layers,
        }

    def to_yaml(self) -> str:
        """Serializa no formato que o ch57x-keyboard-tool consome no stdin."""
        return yaml.dump(
            self.to_yaml_dict(),
            allow_unicode=True,
            default_flow_style=None,
            sort_keys=False,
            width=120,
        )

    @classmethod
    def from_yaml(cls, text: str) -> "Config":
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise ConfigError("O arquivo não contém um mapeamento YAML válido.")

        orientation = str(data.get("orientation", "normal"))
        if orientation not in ORIENTATIONS:
            raise ConfigError(f"Orientação desconhecida: {orientation!r}")

        try:
            rows = int(data.get("rows", 3))
            columns = int(data.get("columns", 4))
            knob_count = int(data.get("knobs", 0))
        except (TypeError, ValueError) as exc:
            raise ConfigError("rows, columns e knobs precisam ser números.") from exc

        if rows < 1 or columns < 1:
            raise ConfigError("rows e columns precisam ser pelo menos 1.")
        if knob_count < 0:
            raise ConfigError("knobs não pode ser negativo.")

        layers = []
        for raw_layer in data.get("layers") or []:
            raw_layer = raw_layer or {}
            buttons = [
                [str(cell) if cell is not None else "" for cell in (row or [])]
                for row in (raw_layer.get("buttons") or [])
            ]
            knobs = [Knob.from_yaml(k) for k in (raw_layer.get("knobs") or [])]
            layers.append(Layer(buttons=buttons, knobs=knobs))

        return cls(
            orientation=orientation,
            rows=rows,
            columns=columns,
            knob_count=knob_count,
            layers=layers,
        )


def default_config() -> Config:
    """Configuração inicial: camada 1 com F13–F24, as outras vazias.

    F13–F24 não colidem com nenhum atalho de sistema, então servem de ponto de
    partida seguro e são fáceis de identificar no assistente de descoberta.
    """
    config = Config()
    for index in range(min(config.button_count, 12)):
        row, column = divmod(index, config.columns)
        config.set(0, row, column, f"f{13 + index}")
    if config.knob_count >= 1:
        config.layers[0].knobs[0] = Knob(ccw="volumedown", press="mute", cw="volumeup")
    if config.knob_count >= 2:
        config.layers[0].knobs[1] = Knob(ccw="prev", press="play", cw="next")
    return config


def is_macro(action: str) -> bool:
    """True quando a ação tem mais de um passo encadeado."""
    return len([p for p in action.split(",") if p.strip()]) > 1


def describe_action(action: str, line_width: int = 11) -> str:
    """Texto para exibir dentro do botão da grade.

    Macros longas quebram em várias linhas (sempre entre passos); o "›" no
    fim da linha indica que a sequência continua.
    """
    action = action.strip()
    if not action:
        return "—"
    parts = [p.strip() for p in action.split(",") if p.strip()]
    if not parts:
        return "—"

    lines: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current} › {part}" if current else part
        if current and len(candidate) > line_width:
            lines.append(current + " ›")
            current = part
        else:
            current = candidate
    lines.append(current)
    return "\n".join(lines)
