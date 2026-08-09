"""Internacionalização: pt-BR (padrão), inglês e espanhol.

Sem dependência do sistema de .qm do Qt — um dicionário simples cobre o app
inteiro e roda igual em qualquer distro. A língua escolhida fica persistida em
~/.config/ch57x_deck/settings.json; sem escolha salva, segue o locale do
sistema.
"""

from __future__ import annotations

import json
import os

from .backend import config_dir

DEFAULT = "pt_BR"

LANGUAGES = {
    "pt_BR": "Português (Brasil)",
    "en": "English",
    "es": "Español",
}

_SETTINGS_FILE = "settings.json"

STRINGS: dict[str, dict[str, str]] = {
    # --- Janela e menus ------------------------------------------------
    "app_title": {
        "pt_BR": "CH57x Deck — Configurador de Macropad",
        "en": "CH57x Deck — Macropad Configurator",
        "es": "CH57x Deck — Configurador de Macropad",
    },
    "menu_file": {"pt_BR": "&Arquivo", "en": "&File", "es": "&Archivo"},
    "menu_open": {"pt_BR": "&Abrir YAML…", "en": "&Open YAML…", "es": "&Abrir YAML…"},
    "menu_save": {"pt_BR": "&Salvar YAML…", "en": "&Save YAML…", "es": "&Guardar YAML…"},
    "menu_quit": {"pt_BR": "Sai&r", "en": "&Quit", "es": "Sali&r"},
    "menu_view_yaml": {
        "pt_BR": "&Ver YAML…",
        "en": "&View YAML…",
        "es": "&Ver YAML…",
    },
    "menu_view": {"pt_BR": "E&xibir", "en": "&View", "es": "&Mostrar"},
    "menu_toggle_test": {
        "pt_BR": "Área de &teste",
        "en": "&Test area",
        "es": "Área de &prueba",
    },
    "menu_language": {"pt_BR": "&Idioma", "en": "&Language", "es": "&Idioma"},
    "menu_theme": {"pt_BR": "&Tema", "en": "&Theme", "es": "&Tema"},
    "theme_dark": {"pt_BR": "Escuro", "en": "Dark", "es": "Oscuro"},
    "theme_light": {"pt_BR": "Claro", "en": "Light", "es": "Claro"},
    "menu_help": {"pt_BR": "A&juda", "en": "&Help", "es": "Ay&uda"},
    "menu_about": {"pt_BR": "&Sobre…", "en": "&About…", "es": "&Acerca de…"},

    # --- Grade ---------------------------------------------------------
    "layer_tab": {"pt_BR": "Camada {n}", "en": "Layer {n}", "es": "Capa {n}"},
    "group_keys": {"pt_BR": "Teclas", "en": "Keys", "es": "Teclas"},
    "group_knobs": {"pt_BR": "Knobs", "en": "Knobs", "es": "Knobs"},
    "knob_n": {"pt_BR": "Knob {n}", "en": "Knob {n}", "es": "Knob {n}"},
    "knob_ccw": {"pt_BR": "Girar ⟲", "en": "Turn ⟲", "es": "Girar ⟲"},
    "knob_press": {"pt_BR": "Apertar", "en": "Press", "es": "Pulsar"},
    "knob_cw": {"pt_BR": "Girar ⟳", "en": "Turn ⟳", "es": "Girar ⟳"},

    # --- Editor ---------------------------------------------------------
    "group_action": {
        "pt_BR": "Ação da seleção",
        "en": "Selected key action",
        "es": "Acción de la selección",
    },
    "group_yaml": {"pt_BR": "YAML gerado", "en": "Generated YAML", "es": "YAML generado"},
    "sel_button": {
        "pt_BR": "Tecla {label}  (camada {layer})",
        "en": "Key {label}  (layer {layer})",
        "es": "Tecla {label}  (capa {layer})",
    },
    "sel_knob": {
        "pt_BR": "Knob {n} — {slot}  (camada {layer})",
        "en": "Knob {n} — {slot}  (layer {layer})",
        "es": "Knob {n} — {slot}  (capa {layer})",
    },
    "tab_keyboard": {"pt_BR": "Teclado", "en": "Keyboard", "es": "Teclado"},
    "tab_media": {"pt_BR": "Mídia", "en": "Media", "es": "Multimedia"},
    "tab_advanced": {"pt_BR": "Avançado", "en": "Advanced", "es": "Avanzado"},
    "combo_none": {"pt_BR": "— nenhuma —", "en": "— none —", "es": "— ninguna —"},
    "btn_add_step": {
        "pt_BR": "Adicionar passo à macro",
        "en": "Add macro step",
        "es": "Añadir paso a la macro",
    },
    "btn_remove_step": {
        "pt_BR": "Remover passo selecionado",
        "en": "Remove selected step",
        "es": "Quitar paso seleccionado",
    },
    "btn_clear": {"pt_BR": "Limpar tecla", "en": "Clear key", "es": "Limpiar tecla"},
    "kb_hint": {
        "pt_BR": (
            "Clique nos modificadores (Ctrl, Shift…) e numa tecla para montar "
            "a combinação. Layout US — no ABNT2 alguns símbolos mudam de lugar "
            "(ex.: o Ç fica na tecla ;)."
        ),
        "en": (
            "Click the modifiers (Ctrl, Shift…) and a key to build the combo. "
            "US layout — on other layouts some symbols sit elsewhere."
        ),
        "es": (
            "Haga clic en los modificadores (Ctrl, Shift…) y en una tecla para "
            "armar la combinación. Distribución US — en otras distribuciones "
            "algunos símbolos cambian de lugar."
        ),
    },
    "chord_tooltip": {
        "pt_BR": "Passos executados em sequência num único aperto (máx. 5).",
        "en": "Steps executed in sequence on a single press (max. 5).",
        "es": "Pasos ejecutados en secuencia con una sola pulsación (máx. 5).",
    },
    "media_hint": {
        "pt_BR": "Teclas de mídia não aceitam modificadores nem macro.",
        "en": "Media keys accept neither modifiers nor macros.",
        "es": "Las teclas multimedia no aceptan modificadores ni macros.",
    },
    "adv_placeholder": {
        "pt_BR": "ex.: ctrl-alt-t  |  click(left)  |  <110>",
        "en": "e.g.: ctrl-alt-t  |  click(left)  |  <110>",
        "es": "ej.: ctrl-alt-t  |  click(left)  |  <110>",
    },
    "adv_hint": {
        "pt_BR": (
            "Expressão livre no dialeto do firmware.\n"
            "Mouse: click(left), wheel(-1), move(5,0), drag(left,0,5)\n"
            "Código bruto: <110>   Macro: ctrl-c,ctrl-v\n\n"
            "O macropad só envia teclas — ele não executa comandos.\n"
            "Para abrir um programa, mapeie uma tecla F13–F24 aqui e crie\n"
            "um atalho de sistema (KDE/GNOME) que rode o comando."
        ),
        "en": (
            "Free-form expression in the firmware dialect.\n"
            "Mouse: click(left), wheel(-1), move(5,0), drag(left,0,5)\n"
            "Raw code: <110>   Macro: ctrl-c,ctrl-v\n\n"
            "The macropad only sends keys — it does not run commands.\n"
            "To launch a program, map an F13–F24 key here and create a\n"
            "system shortcut (KDE/GNOME) that runs the command."
        ),
        "es": (
            "Expresión libre en el dialecto del firmware.\n"
            "Ratón: click(left), wheel(-1), move(5,0), drag(left,0,5)\n"
            "Código bruto: <110>   Macro: ctrl-c,ctrl-v\n\n"
            "El macropad solo envía teclas — no ejecuta comandos.\n"
            "Para abrir un programa, asigne aquí una tecla F13–F24 y cree\n"
            "un atajo de sistema (KDE/GNOME) que ejecute el comando."
        ),
    },

    # --- Grupos de teclas ------------------------------------------------
    "group.letters": {"pt_BR": "Letras", "en": "Letters", "es": "Letras"},
    "group.digits": {"pt_BR": "Números", "en": "Digits", "es": "Números"},
    "group.function": {"pt_BR": "Função", "en": "Function", "es": "Función"},
    "group.navigation": {"pt_BR": "Navegação", "en": "Navigation", "es": "Navegación"},
    "group.punct": {
        "pt_BR": "Pontuação e controle",
        "en": "Punctuation & control",
        "es": "Puntuación y control",
    },
    "group.numpad": {
        "pt_BR": "Teclado numérico",
        "en": "Numeric keypad",
        "es": "Teclado numérico",
    },
    "group.misc": {"pt_BR": "Diversos", "en": "Miscellaneous", "es": "Varios"},

    # --- Área de teste ---------------------------------------------------
    "group_test": {
        "pt_BR": "Área de teste",
        "en": "Test area",
        "es": "Área de prueba",
    },
    "test_placeholder": {
        "pt_BR": "Clique aqui e aperte as teclas do macropad…",
        "en": "Click here and press the macropad keys…",
        "es": "Haga clic aquí y pulse las teclas del macropad…",
    },
    "test_hint": {
        "pt_BR": (
            "Mostra o que cada tecla envia ao sistema. Teclas de mídia/volume "
            "podem ser capturadas pelo desktop antes de chegar aqui."
        ),
        "en": (
            "Shows what each key sends to the system. Media/volume keys may "
            "be grabbed by the desktop before reaching this area."
        ),
        "es": (
            "Muestra lo que cada tecla envía al sistema. Las teclas de "
            "multimedia/volumen pueden ser capturadas por el escritorio antes "
            "de llegar aquí."
        ),
    },
    "btn_clear_log": {"pt_BR": "Limpar", "en": "Clear", "es": "Limpiar"},

    # --- Barra de envio --------------------------------------------------
    "btn_validate": {"pt_BR": "Validar", "en": "Validate", "es": "Validar"},
    "btn_upload": {
        "pt_BR": "Enviar ao macropad",
        "en": "Send to macropad",
        "es": "Enviar al macropad",
    },

    # --- Status e dispositivo -------------------------------------------
    "status_ready": {"pt_BR": "Pronto.", "en": "Ready.", "es": "Listo."},
    "status_valid": {
        "pt_BR": "Configuração válida.",
        "en": "Configuration is valid.",
        "es": "Configuración válida.",
    },
    "status_uploaded": {
        "pt_BR": "Enviado ao macropad com sucesso.",
        "en": "Successfully sent to the macropad.",
        "es": "Enviado al macropad con éxito.",
    },
    "status_opened": {"pt_BR": "Aberto: {name}", "en": "Opened: {name}", "es": "Abierto: {name}"},
    "status_saved": {"pt_BR": "Salvo: {name}", "en": "Saved: {name}", "es": "Guardado: {name}"},
    "dev_no_tool": {
        "pt_BR": "⚠ ch57x-keyboard-tool não encontrado",
        "en": "⚠ ch57x-keyboard-tool not found",
        "es": "⚠ ch57x-keyboard-tool no encontrado",
    },
    "overlay_install_title": {
        "pt_BR": "Ferramenta necessária",
        "en": "Required tool missing",
        "es": "Herramienta necesaria",
    },
    "overlay_install_body": {
        "pt_BR": (
            "O CH57x Deck precisa do ch57x-keyboard-tool para se comunicar "
            "com o macropad. Ele ainda não foi encontrado neste computador."
        ),
        "en": (
            "CH57x Deck needs ch57x-keyboard-tool to talk to the macropad. "
            "It hasn't been found on this computer yet."
        ),
        "es": (
            "CH57x Deck necesita ch57x-keyboard-tool para comunicarse con "
            "el macropad. Aún no se encontró en este equipo."
        ),
    },
    "btn_install_tool": {
        "pt_BR": "Instalar",
        "en": "Install",
        "es": "Instalar",
    },
    "btn_installing": {
        "pt_BR": "Instalando…",
        "en": "Installing…",
        "es": "Instalando…",
    },
    "status_tool_installed": {
        "pt_BR": "ch57x-keyboard-tool instalado com sucesso.",
        "en": "ch57x-keyboard-tool installed successfully.",
        "es": "ch57x-keyboard-tool instalado con éxito.",
    },
    "dlg_install_fail": {
        "pt_BR": "Falha ao instalar",
        "en": "Installation failed",
        "es": "Fallo al instalar",
    },
    "dev_absent": {
        "pt_BR": "⚠ Macropad não detectado (USB 1189)",
        "en": "⚠ Macropad not detected (USB 1189)",
        "es": "⚠ Macropad no detectado (USB 1189)",
    },
    "dev_connected": {
        "pt_BR": "● Macropad conectado",
        "en": "● Macropad connected",
        "es": "● Macropad conectado",
    },
    "dev_no_access": {
        "pt_BR": "⚠ Macropad detectado, mas sem permissão USB",
        "en": "⚠ Macropad detected, but no USB permission",
        "es": "⚠ Macropad detectado, pero sin permiso USB",
    },

    # --- Diálogos --------------------------------------------------------
    "dlg_open_title": {
        "pt_BR": "Abrir configuração",
        "en": "Open configuration",
        "es": "Abrir configuración",
    },
    "dlg_save_title": {
        "pt_BR": "Salvar configuração",
        "en": "Save configuration",
        "es": "Guardar configuración",
    },
    "dlg_open_error": {"pt_BR": "Erro ao abrir", "en": "Error opening file", "es": "Error al abrir"},
    "dlg_invalid": {
        "pt_BR": "Configuração inválida",
        "en": "Invalid configuration",
        "es": "Configuración inválida",
    },
    "dlg_upload_fail": {"pt_BR": "Falha no envio", "en": "Upload failed", "es": "Fallo en el envío"},
    "udev_hint": {
        "pt_BR": (
            "\n\nSem permissão no USB. Instale a regra udev:\n"
            "sudo cp udev/70-macropad-ch57x.rules /etc/udev/rules.d/\n"
            "sudo udevadm control --reload-rules && sudo udevadm trigger"
        ),
        "en": (
            "\n\nNo USB permission. Install the udev rule:\n"
            "sudo cp udev/70-macropad-ch57x.rules /etc/udev/rules.d/\n"
            "sudo udevadm control --reload-rules && sudo udevadm trigger"
        ),
        "es": (
            "\n\nSin permiso en el USB. Instale la regla udev:\n"
            "sudo cp udev/70-macropad-ch57x.rules /etc/udev/rules.d/\n"
            "sudo udevadm control --reload-rules && sudo udevadm trigger"
        ),
    },
    "dlg_perm_title": {
        "pt_BR": "Permissão USB",
        "en": "USB permission",
        "es": "Permiso USB",
    },
    "dlg_perm_text": {
        "pt_BR": (
            "O macropad foi detectado, mas seu usuário ainda não tem permissão "
            "para gravar nele.\n\n"
            "Instalar agora a regra de sistema (udev) que libera o acesso? "
            "A senha de administrador será pedida uma única vez."
        ),
        "en": (
            "The macropad was detected, but your user does not yet have "
            "permission to write to it.\n\n"
            "Install the system (udev) rule that grants access now? "
            "The administrator password will be asked only once."
        ),
        "es": (
            "El macropad fue detectado, pero su usuario aún no tiene permiso "
            "para escribir en él.\n\n"
            "¿Instalar ahora la regla de sistema (udev) que concede el acceso? "
            "La contraseña de administrador se pedirá una sola vez."
        ),
    },
    "btn_install_rule": {
        "pt_BR": "Instalar agora",
        "en": "Install now",
        "es": "Instalar ahora",
    },
    "btn_later": {"pt_BR": "Depois", "en": "Later", "es": "Más tarde"},
    "perm_ok": {
        "pt_BR": "Permissão USB configurada com sucesso.",
        "en": "USB permission configured successfully.",
        "es": "Permiso USB configurado con éxito.",
    },
    "perm_replug": {
        "pt_BR": (
            "Regra instalada, mas o acesso ainda não liberou. "
            "Desconecte e reconecte o macropad."
        ),
        "en": (
            "Rule installed, but access has not taken effect yet. "
            "Unplug and replug the macropad."
        ),
        "es": (
            "Regla instalada, pero el acceso aún no se aplicó. "
            "Desconecte y reconecte el macropad."
        ),
    },
    "perm_fail": {
        "pt_BR": "A instalação da regra falhou:\n{msg}",
        "en": "Installing the rule failed:\n{msg}",
        "es": "La instalación de la regla falló:\n{msg}",
    },
    "invalid_action_button": {
        "pt_BR": (
            "A ação “{action}” na tecla {label} (camada {layer}) não é uma "
            "tecla válida do firmware."
        ),
        "en": (
            "The action “{action}” on key {label} (layer {layer}) is not a "
            "valid firmware key."
        ),
        "es": (
            "La acción “{action}” en la tecla {label} (capa {layer}) no es "
            "una tecla válida del firmware."
        ),
    },
    "invalid_action_knob": {
        "pt_BR": (
            "A ação “{action}” no knob {n} ({slot}, camada {layer}) não é "
            "válida para o firmware."
        ),
        "en": (
            "The action “{action}” on knob {n} ({slot}, layer {layer}) is "
            "not valid for the firmware."
        ),
        "es": (
            "La acción “{action}” en el knob {n} ({slot}, capa {layer}) no "
            "es válida para el firmware."
        ),
    },
    "invalid_action_hint": {
        "pt_BR": (
            "O macropad só envia teclas — ele não abre programas nem executa "
            "comandos.\n\n"
            "Para abrir um programa (ex.: kcalc):\n"
            "1. Mapeie esta tecla como F13–F24 (aba Teclado → grupo Função) "
            "e envie ao macropad.\n"
            "2. No KDE: Configurações do Sistema → Teclado → Atalhos → "
            "Adicionar novo → Comando ou script… → digite o comando.\n"
            "3. No atalho criado, aperte a tecla física do macropad."
        ),
        "en": (
            "The macropad only sends keys — it cannot launch programs or run "
            "commands.\n\n"
            "To launch a program (e.g. kcalc):\n"
            "1. Map this key as F13–F24 (Keyboard tab → Function group) and "
            "send it to the macropad.\n"
            "2. In your desktop: System Settings → Keyboard → Shortcuts → "
            "Add new → Command or script… → type the command.\n"
            "3. In the new shortcut, press the physical macropad key."
        ),
        "es": (
            "El macropad solo envía teclas — no puede abrir programas ni "
            "ejecutar comandos.\n\n"
            "Para abrir un programa (ej.: kcalc):\n"
            "1. Asigne esta tecla como F13–F24 (pestaña Teclado → grupo "
            "Función) y envíela al macropad.\n"
            "2. En el escritorio: Preferencias del Sistema → Teclado → "
            "Atajos → Añadir nuevo → Comando o script… → escriba el comando.\n"
            "3. En el atajo creado, pulse la tecla física del macropad."
        ),
    },
    "yaml_filter": {
        "pt_BR": "YAML (*.yaml *.yml)",
        "en": "YAML (*.yaml *.yml)",
        "es": "YAML (*.yaml *.yml)",
    },

    # --- Sobre -----------------------------------------------------------
    "about_title": {
        "pt_BR": "Sobre o CH57x Deck",
        "en": "About CH57x Deck",
        "es": "Acerca de CH57x Deck",
    },
    "about_text": {
        "pt_BR": (
            "<h3>CH57x Deck</h3>"
            "<p>Versão {version}</p>"
            "<p>Criado por <b>Péricles Sávio</b>.</p>"
            "<p>Frontend gráfico para o "
            "<a href='https://github.com/kriomant/ch57x-keyboard-tool' "
            "style='color:{link_color}'>ch57x-keyboard-tool</a>: monta a "
            "configuração do macropad numa interface visual e delega a esse "
            "binário toda a comunicação USB (validação e gravação no "
            "firmware do dispositivo).</p>"
        ),
        "en": (
            "<h3>CH57x Deck</h3>"
            "<p>Version {version}</p>"
            "<p>Created by <b>Péricles Sávio</b>.</p>"
            "<p>Graphical frontend for "
            "<a href='https://github.com/kriomant/ch57x-keyboard-tool' "
            "style='color:{link_color}'>ch57x-keyboard-tool</a>: builds the "
            "macropad configuration in a visual interface and delegates all "
            "USB communication (validation and writing to the device "
            "firmware) to that binary.</p>"
        ),
        "es": (
            "<h3>CH57x Deck</h3>"
            "<p>Versión {version}</p>"
            "<p>Creado por <b>Péricles Sávio</b>.</p>"
            "<p>Frontend gráfico para "
            "<a href='https://github.com/kriomant/ch57x-keyboard-tool' "
            "style='color:{link_color}'>ch57x-keyboard-tool</a>: arma la "
            "configuración del macropad en una interfaz visual y delega en "
            "ese binario toda la comunicación USB (validación y grabación "
            "en el firmware del dispositivo).</p>"
        ),
    },
}


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
