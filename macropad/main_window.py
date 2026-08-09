"""Janela principal: grade do macropad, camadas, editor e envio ao dispositivo."""

from __future__ import annotations

import re
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QColor, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from . import __version__, model, settings, theme
from .action_editor import ActionEditor
from .backend import Backend, config_dir
from .i18n import LANGUAGES, current_language, set_language, tr
from .test_area import TestArea

# (slot no modelo, chave de tradução do rótulo)
_KNOB_SLOTS = [("ccw", "knob_ccw"), ("press", "knob_press"), ("cw", "knob_cw")]

# Padrões do erro do ch57x-keyboard-tool apontando a ação inválida.
_BUTTON_ERR = re.compile(r"layers\[(\d+)\]\.buttons\[(\d+)\]\[(\d+)\]")
_KNOB_ERR = re.compile(r"layers\[(\d+)\]\.knobs\[(\d+)\]\.(ccw|press|cw)")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(tr("app_title"))
        self.resize(1400, 855)

        self.backend = Backend()
        self.config = self._load_last_config()
        self.current_layer = 0
        # Seleção atual: ("button", linha, coluna) ou ("knob", índice, slot)
        self.selection: tuple[str, int, int | str] | None = None
        self._dirty = False
        self._theme_mode = settings.get("theme", theme.DEFAULT_THEME)

        self._build_menu()
        self._build_ui()
        self._select_button(0, 0)
        self._refresh_device_status()

        # Situação do dispositivo re-checada de tempos em tempos.
        self._device_timer = QTimer(self)
        self._device_timer.timeout.connect(self._refresh_device_status)
        self._device_timer.start(3000)

        # Se o macropad estiver conectado mas sem permissão de acesso,
        # oferece instalar a regra udev logo na abertura (uma vez por sessão).
        self._permission_offered = False
        QTimer.singleShot(600, self._maybe_offer_permission)

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        menu = self.menuBar().addMenu(tr("menu_file"))

        open_action = QAction(tr("menu_open"), self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        menu.addAction(open_action)

        save_action = QAction(tr("menu_save"), self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        menu.addAction(save_action)

        menu.addSeparator()
        yaml_action = QAction(tr("menu_view_yaml"), self)
        yaml_action.triggered.connect(self._show_yaml)
        menu.addAction(yaml_action)

        menu.addSeparator()
        quit_action = QAction(tr("menu_quit"), self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

        view_menu = self.menuBar().addMenu(tr("menu_view"))
        self._test_area_action = QAction(tr("menu_toggle_test"), self)
        self._test_area_action.setCheckable(True)
        self._test_area_action.setChecked(settings.get("show_test_area", False))
        self._test_area_action.toggled.connect(self._toggle_test_area)
        view_menu.addAction(self._test_area_action)

        theme_menu = self.menuBar().addMenu(tr("menu_theme"))
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        for mode, label_key in [("dark", "theme_dark"), ("light", "theme_light")]:
            action = QAction(tr(label_key), self)
            action.setCheckable(True)
            action.setChecked(mode == self._theme_mode)
            action.triggered.connect(
                lambda _=False, mode=mode: self._change_theme(mode)
            )
            theme_group.addAction(action)
            theme_menu.addAction(action)

        lang_menu = self.menuBar().addMenu(tr("menu_language"))
        for code, label in LANGUAGES.items():
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(code == current_language())
            action.triggered.connect(
                lambda _=False, code=code: self._change_language(code)
            )
            lang_menu.addAction(action)

        help_menu = self.menuBar().addMenu(tr("menu_help"))
        about_action = QAction(tr("menu_about"), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_ui(self) -> None:
        central = QWidget()
        outer = QHBoxLayout(central)

        # Coluna principal (camadas, grade, editor, envio); a área de teste
        # vive numa coluna própria à direita, com a altura toda da janela.
        root = QVBoxLayout()
        outer.addLayout(root, stretch=4)

        self._test_area = TestArea()
        self._test_area.setMinimumWidth(240)
        self._test_area.setVisible(self._test_area_action.isChecked())
        outer.addWidget(self._test_area, stretch=1)

        # O YAML gerado vive numa janela separada (menu Arquivo → Ver YAML),
        # sempre atualizada junto com a configuração.
        self._yaml_dialog = QDialog(self)
        self._yaml_dialog.setWindowTitle(tr("group_yaml"))
        self._yaml_dialog.resize(440, 560)
        yaml_layout = QVBoxLayout(self._yaml_dialog)
        self._yaml_view = QPlainTextEdit()
        self._yaml_view.setReadOnly(True)
        yaml_layout.addWidget(self._yaml_view)

        # --- Camadas -------------------------------------------------
        self._layer_bar = QTabBar()
        for i in range(model.LAYER_COUNT):
            self._layer_bar.addTab(tr("layer_tab", n=i + 1))
        self._layer_bar.currentChanged.connect(self._layer_changed)
        root.addWidget(self._layer_bar)

        # --- Grade + knobs ------------------------------------------
        # As caixas expandem junto com a largura da janela (proporção 4:3,
        # acompanhando o número de colunas de botões de cada uma).
        pad_row = QHBoxLayout()

        self._pad_group = QButtonGroup(self)
        self._pad_group.setExclusive(True)

        grid_box = QGroupBox(tr("group_keys"))
        grid = QGridLayout(grid_box)
        grid.setSpacing(6)
        self._pad_buttons: list[list[QPushButton]] = []
        for r in range(self.config.rows):
            row_buttons = []
            for c in range(self.config.columns):
                btn = QPushButton()
                btn.setProperty("role", "pad")
                btn.setCheckable(True)
                btn.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                )
                btn.clicked.connect(
                    lambda _=False, r=r, c=c: self._select_button(r, c)
                )
                self._pad_group.addButton(btn)
                grid.addWidget(btn, r, c)
                row_buttons.append(btn)
            self._pad_buttons.append(row_buttons)
        for c in range(self.config.columns):
            grid.setColumnStretch(c, 1)
        pad_row.addWidget(grid_box, stretch=4)

        if self.config.knob_count:
            knob_box = QGroupBox(tr("group_knobs"))
            knob_layout = QVBoxLayout(knob_box)
            self._knob_buttons: dict[tuple[int, str], QPushButton] = {}
            for k in range(self.config.knob_count):
                if k:
                    # Espaço elástico entre os knobs: o primeiro fica no topo
                    # e o último na base, espelhando o dispositivo físico.
                    knob_layout.addStretch()
                knob_layout.addWidget(QLabel(tr("knob_n", n=k + 1)))
                slot_row = QHBoxLayout()
                for slot, label_key in _KNOB_SLOTS:
                    btn = QPushButton(tr(label_key))
                    btn.setProperty("role", "knob")
                    btn.setCheckable(True)
                    btn.setSizePolicy(
                        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                    )
                    btn.clicked.connect(
                        lambda _=False, k=k, s=slot: self._select_knob(k, s)
                    )
                    self._pad_group.addButton(btn)
                    self._knob_buttons[(k, slot)] = btn
                    slot_row.addWidget(btn)
                knob_layout.addLayout(slot_row)
            pad_row.addSpacing(24)
            pad_row.addWidget(knob_box, stretch=3)

        root.addLayout(pad_row)

        # --- Editor + YAML ------------------------------------------
        bottom = QHBoxLayout()

        editor_box = QGroupBox(tr("group_action"))
        editor_layout = QVBoxLayout(editor_box)
        self._selection_label = QLabel()
        self._selection_label.setProperty("role", "heading")
        self.editor = ActionEditor()
        self.editor.action_changed.connect(self._action_edited)
        editor_layout.addWidget(self._selection_label)
        editor_layout.addWidget(self.editor, stretch=1)
        bottom.addWidget(editor_box, stretch=3)

        root.addLayout(bottom, stretch=1)

        # --- Barra de envio -----------------------------------------
        send_row = QHBoxLayout()

        self._device_label = QLabel()
        self._device_label.setProperty("role", "dim")
        send_row.addWidget(self._device_label)
        send_row.addStretch()

        validate_btn = QPushButton(tr("btn_validate"))
        validate_btn.clicked.connect(self._validate)
        send_row.addWidget(validate_btn)

        self._upload_btn = QPushButton(tr("btn_upload"))
        self._upload_btn.setProperty("role", "accent")
        self._upload_btn.clicked.connect(self._upload)
        send_row.addWidget(self._upload_btn)

        root.addLayout(send_row)

        # A "página" normal e o overlay de instalação ocupam o mesmo espaço,
        # empilhados (StackAll) — o overlay fica por cima e escurece o resto
        # quando visível, sem precisar de uma janela separada.
        self._install_overlay = self._build_install_overlay()
        container = QWidget()
        stack = QStackedLayout(container)
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        stack.addWidget(central)
        stack.addWidget(self._install_overlay)
        stack.setCurrentWidget(self._install_overlay)

        self.setCentralWidget(container)
        self.statusBar().showMessage(tr("status_ready"))

    def _build_install_overlay(self) -> QWidget:
        """Fundo escurecido + card central pedindo para instalar o binário."""
        overlay = QWidget()
        overlay.setObjectName("installOverlay")
        overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        overlay.hide()

        card = QFrame()
        card.setObjectName("installCard")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setFixedWidth(380)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 190))
        card.setGraphicsEffect(shadow)

        icon = QLabel("⚠")
        icon.setProperty("role", "dangerIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(tr("overlay_install_title"))
        title.setProperty("role", "heading")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)

        body = QLabel(tr("overlay_install_body"))
        body.setProperty("role", "dim")
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.setWordWrap(True)

        self._install_tool_btn = QPushButton(tr("btn_install_tool"))
        self._install_tool_btn.setProperty("role", "danger")
        self._install_tool_btn.clicked.connect(self._install_tool)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(10)
        card_layout.addWidget(icon)
        card_layout.addWidget(title)
        card_layout.addWidget(body)
        card_layout.addSpacing(6)
        card_layout.addWidget(
            self._install_tool_btn, alignment=Qt.AlignmentFlag.AlignCenter
        )

        outer = QVBoxLayout(overlay)
        outer.addStretch()
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(card)
        row.addStretch()
        outer.addLayout(row)
        outer.addStretch()

        return overlay

    # ------------------------------------------------------------------
    # Seleção e edição
    # ------------------------------------------------------------------

    def _select_button(self, row: int, column: int) -> None:
        self.selection = ("button", row, column)
        self._pad_buttons[row][column].setChecked(True)
        label = self.config.button_label(row, column)
        self._selection_label.setText(
            tr("sel_button", label=label, layer=self.current_layer + 1)
        )
        self.editor.set_action(self.config.get(self.current_layer, row, column))

    def _select_knob(self, knob: int, slot: str) -> None:
        self.selection = ("knob", knob, slot)
        self._knob_buttons[(knob, slot)].setChecked(True)
        slot_label = tr(dict(_KNOB_SLOTS)[slot])
        self._selection_label.setText(
            tr("sel_knob", n=knob + 1, slot=slot_label, layer=self.current_layer + 1)
        )
        action = getattr(self.config.layers[self.current_layer].knobs[knob], slot)
        self.editor.set_action(action)

    def _action_edited(self, action: str) -> None:
        if not self.selection:
            return
        kind, a, b = self.selection
        if kind == "button":
            self.config.set(self.current_layer, a, b, action)
        else:
            setattr(self.config.layers[self.current_layer].knobs[a], b, action)
        self._dirty = True
        self._refresh_pad_labels()
        self._refresh_yaml()

    def _layer_changed(self, index: int) -> None:
        self.current_layer = index
        self._refresh_pad_labels()
        # Recarrega a seleção atual no contexto da nova camada.
        if self.selection:
            kind, a, b = self.selection
            if kind == "button":
                self._select_button(a, b)
            else:
                self._select_knob(a, b)

    # ------------------------------------------------------------------
    # Atualização visual
    # ------------------------------------------------------------------

    def _refresh_pad_labels(self) -> None:
        for r, row_buttons in enumerate(self._pad_buttons):
            for c, btn in enumerate(row_buttons):
                action = self.config.get(self.current_layer, r, c)
                label = self.config.button_label(r, c)
                if model.is_macro(action):
                    label += "  · macro"
                btn.setText(f"{label}\n{model.describe_action(action)}")
                btn.setToolTip(action if model.is_macro(action) else "")
        if self.config.knob_count:
            for (k, slot), btn in self._knob_buttons.items():
                action = getattr(self.config.layers[self.current_layer].knobs[k], slot)
                slot_label = tr(dict(_KNOB_SLOTS)[slot])
                if model.is_macro(action):
                    slot_label += "  · macro"
                btn.setText(f"{slot_label}\n{model.describe_action(action)}")
                btn.setToolTip(action if model.is_macro(action) else "")

    def _refresh_yaml(self) -> None:
        self._yaml_view.setPlainText(self.config.to_yaml())

    def _show_yaml(self) -> None:
        self._refresh_yaml()
        self._yaml_dialog.show()
        self._yaml_dialog.raise_()
        self._yaml_dialog.activateWindow()

    def _refresh_device_status(self) -> None:
        tool = self.backend.find_tool()
        present = self.backend.device_present()
        if not tool:
            self._device_label.setText(tr("dev_no_tool"))
        elif not present:
            self._device_label.setText(tr("dev_absent"))
        elif not self.backend.device_accessible():
            self._device_label.setText(tr("dev_no_access"))
        else:
            self._device_label.setText(tr("dev_connected"))
        self._upload_btn.setEnabled(bool(tool) and present)
        # Só oferece instalar quando falta o binário e existe release pronta
        # para esta arquitetura (x86_64/aarch64); fora isso, sem overlay.
        self._install_overlay.setVisible(
            not tool and self.backend.download_url() is not None
        )

    def _install_tool(self) -> None:
        self._install_tool_btn.setEnabled(False)
        self._install_tool_btn.setText(tr("btn_installing"))
        QApplication.processEvents()
        try:
            self.backend.install_tool()
        except RuntimeError as exc:
            QMessageBox.critical(self, tr("dlg_install_fail"), str(exc))
        else:
            self.statusBar().showMessage(tr("status_tool_installed"))
        finally:
            self._install_tool_btn.setText(tr("btn_install_tool"))
            self._install_tool_btn.setEnabled(True)
            self._refresh_device_status()

    # ------------------------------------------------------------------
    # Arquivo
    # ------------------------------------------------------------------

    def _autosave_path(self) -> Path:
        return config_dir() / "current.yaml"

    def _load_last_config(self) -> model.Config:
        path = config_dir() / "current.yaml"
        if path.is_file():
            try:
                return model.Config.from_yaml(path.read_text())
            except (OSError, model.ConfigError):
                pass
        return model.default_config()

    def _autosave(self) -> None:
        path = self._autosave_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.config.to_yaml())

    def _open_file(self) -> None:
        name, _ = QFileDialog.getOpenFileName(
            self, tr("dlg_open_title"), "", tr("yaml_filter")
        )
        if not name:
            return
        try:
            self.config = model.Config.from_yaml(Path(name).read_text())
        except (OSError, model.ConfigError) as exc:
            QMessageBox.critical(self, tr("dlg_open_error"), str(exc))
            return
        self._dirty = True
        self._layer_bar.setCurrentIndex(0)
        self.current_layer = 0
        self._refresh_pad_labels()
        self._refresh_yaml()
        self._select_button(0, 0)
        self.statusBar().showMessage(tr("status_opened", name=name))

    def _save_file(self) -> None:
        name, _ = QFileDialog.getSaveFileName(
            self, tr("dlg_save_title"), "macropad.yaml", tr("yaml_filter")
        )
        if not name:
            return
        Path(name).write_text(self.config.to_yaml())
        self.statusBar().showMessage(tr("status_saved", name=name))

    # ------------------------------------------------------------------
    # Dispositivo
    # ------------------------------------------------------------------

    def _show_invalid_config(self, message: str) -> None:
        """Traduz o erro do validador para algo acionável, focando a ação errada."""
        friendly = None
        if match := _BUTTON_ERR.search(message):
            layer, row, col = (int(g) for g in match.groups())
            self._layer_bar.setCurrentIndex(layer)
            self._select_button(row, col)
            friendly = tr(
                "invalid_action_button",
                action=self.config.get(layer, row, col),
                label=self.config.button_label(row, col),
                layer=layer + 1,
            )
        elif match := _KNOB_ERR.search(message):
            layer, knob = int(match.group(1)), int(match.group(2))
            slot = match.group(3)
            self._layer_bar.setCurrentIndex(layer)
            self._select_knob(knob, slot)
            friendly = tr(
                "invalid_action_knob",
                action=getattr(self.config.layers[layer].knobs[knob], slot),
                n=knob + 1,
                slot=tr(dict(_KNOB_SLOTS)[slot]),
                layer=layer + 1,
            )

        box = QMessageBox(self)
        box.setWindowTitle(tr("dlg_invalid"))
        box.setIcon(QMessageBox.Icon.Warning)
        if friendly:
            box.setText(friendly + "\n\n" + tr("invalid_action_hint"))
            box.setDetailedText(message)
        else:
            box.setText(message)
        box.exec()

    def _validate(self) -> None:
        result = self.backend.validate(self.config.to_yaml())
        if result.ok:
            self.statusBar().showMessage(tr("status_valid"))
        else:
            self._show_invalid_config(result.message)

    def _upload(self) -> None:
        yaml_text = self.config.to_yaml()
        result = self.backend.validate(yaml_text)
        if not result.ok:
            self._show_invalid_config(result.message)
            return
        result = self.backend.upload(yaml_text)
        if result.ok:
            self._autosave()
            self._dirty = False
            self.statusBar().showMessage(tr("status_uploaded"))
        else:
            msg = result.message
            denied = "Access denied" in msg or "Permission denied" in msg
            if denied and self.backend.can_install_udev_rule():
                # Em vez de mandar o usuário ao terminal, oferece resolver aqui.
                self._offer_permission_setup()
                return
            if denied:
                msg += tr("udev_hint")
            QMessageBox.critical(self, tr("dlg_upload_fail"), msg)

    def _toggle_test_area(self, visible: bool) -> None:
        self._test_area.setVisible(visible)
        settings.save("show_test_area", visible)

    # ------------------------------------------------------------------
    # Permissão USB (regra udev)
    # ------------------------------------------------------------------

    def _maybe_offer_permission(self) -> None:
        """Na abertura: se o macropad está presente mas inacessível, oferece
        instalar a regra udev — a senha é pedida pelo diálogo do sistema."""
        if self._permission_offered or not self.backend.device_present():
            return
        if self.backend.device_accessible():
            return
        if not self.backend.can_install_udev_rule():
            return  # sem pkexec, o erro de envio mostra os comandos manuais
        self._offer_permission_setup()

    def _offer_permission_setup(self) -> None:
        self._permission_offered = True
        box = QMessageBox(self)
        box.setWindowTitle(tr("dlg_perm_title"))
        box.setIcon(QMessageBox.Icon.Question)
        box.setText(tr("dlg_perm_text"))
        install = box.addButton(
            tr("btn_install_rule"), QMessageBox.ButtonRole.AcceptRole
        )
        box.addButton(tr("btn_later"), QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() is install:
            self._install_permission()

    def _install_permission(self) -> None:
        result = self.backend.install_udev_rule()
        if not result.ok:
            # 126/127 = usuário cancelou/senha errada no diálogo do polkit;
            # nesse caso não vale a pena empilhar outro diálogo de erro.
            if result.message:
                QMessageBox.warning(
                    self, tr("dlg_perm_title"), tr("perm_fail", msg=result.message)
                )
            return
        # O `udevadm trigger` reaplica a ACL sem reconectar; dá um instante
        # para o udev processar antes de conferir.
        QTimer.singleShot(1200, self._confirm_permission)

    def _confirm_permission(self) -> None:
        self._refresh_device_status()
        if self.backend.device_accessible():
            self.statusBar().showMessage(tr("perm_ok"))
        else:
            QMessageBox.information(
                self, tr("dlg_perm_title"), tr("perm_replug")
            )

    # ------------------------------------------------------------------
    # Tema, idioma e Sobre
    # ------------------------------------------------------------------

    def _change_theme(self, mode: str) -> None:
        if mode == self._theme_mode:
            return
        self._theme_mode = mode
        settings.save("theme", mode)
        # Estilo é global (QApplication); reaplicar re-poli todos os widgets
        # já existentes na hora, sem precisar reconstruir a janela.
        QApplication.instance().setStyleSheet(theme.stylesheet_for(mode))

    def _change_language(self, code: str) -> None:
        if code == current_language():
            return
        set_language(code)
        # Reconstrói a janela na nova língua, preservando config e geometria.
        self._autosave()
        new_window = MainWindow()
        new_window.setGeometry(self.geometry())
        new_window.show()
        QApplication.instance()._main_window = new_window
        self.close()

    def _show_about(self) -> None:
        link_color = theme.PALETTES[self._theme_mode].ACCENT
        QMessageBox.about(
            self,
            tr("about_title"),
            tr("about_text", version=__version__, link_color=link_color),
        )

    # ------------------------------------------------------------------

    def showEvent(self, event) -> None:  # noqa: N802 (API Qt)
        super().showEvent(event)
        self._refresh_pad_labels()
        self._refresh_yaml()

    def closeEvent(self, event) -> None:  # noqa: N802 (API Qt)
        self._autosave()
        super().closeEvent(event)
