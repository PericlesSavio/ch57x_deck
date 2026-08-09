[English](README.md) | [Português](README.pt-BR.md) | Español

# CH57x Deck

**Frontend gráfico (Qt/PySide6) para
[ch57x-keyboard-tool](https://github.com/kriomant/ch57x-keyboard-tool)** —
CH57x Deck no se comunica con el macropad directamente; arma la
configuración en una interfaz visual y delega toda la comunicación USB
(validación y grabación) a ese binario de línea de comandos, invocándolo
como subproceso. Sin ch57x-keyboard-tool instalado, la app funciona pero no
puede grabar nada (por eso ofrece instalarlo automáticamente — ver
"Requisitos").

Sirve para configurar macropads basados en el chip CH57x (VID USB `1189`,
PIDs `8840`/`8842`/`8890` — los modelos genéricos de 3/6/9/12/15 teclas con
knobs). La grabación se hace **en el firmware del dispositivo**: una vez
enviada, la asignación funciona en cualquier computadora, sin necesitar esta
app ni un daemon en ejecución.

## Hardware

![Macropad probado](assets/macropad-hardware.png)

La unidad de la foto es un macropad CH57x genérico con RGB, dos knobs y
cable USB desmontable — este tipo de dispositivo, vendido bajo varias
marcas distintas, es el objetivo de CH57x Deck.

## Requisitos

- Linux con systemd/udev (Fedora, Ubuntu/Debian, Arch, openSUSE…)
- Python 3.10+
- El PySide6 instalado vía pip exige **glibc ≥ 2.34** (el wheel incluye su
  propio Qt, y ese es su piso). Satisfecho por las versiones actuales —
  Fedora 35+, Ubuntu 22.04+, Debian 12+, RHEL/Rocky/Alma 9+, Arch, openSUSE
  Tumbleweed. En LTS más antiguas aún en uso (Ubuntu 20.04, Debian 11,
  RHEL/Rocky/Alma 8), instale PySide6 desde el paquete de la propia distro
  en vez de pip — ej.: `apt install python3-pyside6.qtwidgets`, `dnf
  install python3-pyside6`, `pacman -S pyside6` — y luego instale CH57x
  Deck normalmente; detectará y reutilizará esa copia en vez de descargar
  el wheel de pip.
- `ch57x-keyboard-tool`: si no está en el PATH, la propia app ofrece
  descargar la versión oficial en la primera ejecución (en
  `~/.local/share/ch57x_deck/bin`)

## Instalación

```bash
./install.sh
```

Instala la app (pip, a nivel de usuario, sin root), el ícono y el acceso
directo en el menú de aplicaciones y — preguntando antes — la regla udev
para el permiso USB sin root. Se ejecuta como usuario normal; `sudo` solo
se usa en ese último paso, opcional. Para quitar todo lo instalado:

```bash
./install.sh --uninstall
```

(pregunta antes de borrar su configuración guardada; el resto se quita sin
preguntar).

### Instalación manual

Si prefiere hacerlo a mano, o solo quiere el comando `ch57x-deck` sin la
integración con el escritorio:

```bash
pip install --user -e .
```

Esto instala las dependencias (PySide6, PyYAML) y crea el comando
`ch57x-deck` en `~/.local/bin` (debe estar en el `PATH`, lo cual ya es el
predeterminado en la mayoría de las distros). `-e` deja el paquete
"editable": los cambios en los archivos de `macropad/` se aplican al
instante, sin reinstalar — útil durante el desarrollo; para un uso
puramente final, da igual usar `-e` o no.

<details>
<summary>Ícono, acceso directo y permiso USB, a mano</summary>

```bash
# Ícono y acceso directo en el menú de aplicaciones
cp assets/ch57x-deck.svg ~/.local/share/icons/hicolor/scalable/apps/
cp assets/ch57x-deck.desktop ~/.local/share/applications/
gtk-update-icon-cache ~/.local/share/icons/hicolor 2>/dev/null
update-desktop-database ~/.local/share/applications 2>/dev/null

# Permiso USB (root, una sola vez)
sudo cp udev/70-macropad-ch57x.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

La app también ofrece instalar la regla udev por sí sola, vía `pkexec`, si
detecta el macropad sin permiso.

</details>

## Uso

```bash
ch57x-deck
```

Sin instalar (por ejemplo, solo para probar), también se puede ejecutar
directamente desde el repositorio con `python run.py`.

1. Elija la **capa** (el macropad tiene 3, alternadas con el botón lateral).
2. Haga clic en una **tecla o función de knob** en la grilla.
3. Arme la acción en el editor:
   - **Teclado** — modificadores + tecla; hasta 5 pasos encadenados
     (macro).
   - **Multimedia** — reproducir/pausar, volumen, etc. (el firmware no
     permite modificadores junto con teclas multimedia).
   - **Avanzado** — expresión libre: ratón (`click(left)`, `wheel(-1)`),
     código bruto (`<110>`), macros manuales (`ctrl-c,ctrl-v`).
4. **Validar** revisa el YAML; **Enviar al macropad** lo graba en el
   firmware.

La última configuración enviada queda en
`~/.config/ch57x_deck/current.yaml` (y se recarga al abrir la app).
`Archivo → Guardar/Abrir` exporta e importa YAML compatible con el
`ch57x-keyboard-tool` puro.

## Planes futuros

- **Soporte para las variantes de 3/6/9/15 teclas y 0–3 knobs.** El backend
  (ch57x-keyboard-tool) y el modelo YAML ya aceptan cualquier geometría;
  falta que la interfaz reconstruya la grilla cuando cambia la geometría y
  ofrezca un menú "Modelo de macropad" (la geometría no es detectable por
  USB). Hoy la UI asume 3×4 + 2 knobs, y abrir un YAML con otra geometría
  falla (`IndexError` en `_refresh_pad_labels`).
- **Pruebas automatizadas** (pytest) para `model.py` (serialización YAML) y
  `keys.py` (validación de acciones) — hoy toda la verificación es manual.
- **Perfiles con nombre.** Hoy solo existe una configuración autoguardada
  (`current.yaml`); `Archivo → Guardar/Abrir` cubre la importación/
  exportación manual, pero no un cambio rápido entre perfiles (ej.:
  "Trabajo" vs. "Juego") directo desde el menú.
- **Elegir una licencia** antes de publicar el repositorio públicamente —
  aún no definida.

### Limitación conocida (no es posible hoy)

**Leer la asignación ya grabada en el macropad.** El `ch57x-keyboard-tool`
solo expone `upload` (grabar), no un comando de lectura — no hay forma de
"importar" lo que ya está en el dispositivo, solo reconstruirlo a partir de
un YAML guardado localmente.

## Estructura

| Archivo | Función |
| --- | --- |
| `macropad/model.py` | Config en memoria + (de)serialización YAML |
| `macropad/keys.py` | Catálogo de teclas/modificadores del firmware |
| `macropad/backend.py` | Llama a ch57x-keyboard-tool; detecta el USB vía sysfs |
| `macropad/action_editor.py` | Widget de edición de una acción |
| `macropad/keyboard_widget.py` | Teclado visual clicable |
| `macropad/test_area.py` | Área de prueba (captura lo que envía el pad) |
| `macropad/main_window.py` | Ventana principal |
| `macropad/i18n.py` | Traducciones (pt-BR, en, es) |
| `macropad/settings.py` | Preferencias persistentes |
| `macropad/theme.py` | Tema Monokai (gris oscuro, esquinas rectas) |
| `udev/70-macropad-ch57x.rules` | Regla de permiso USB |
| `pyproject.toml` | Empaquetado; genera el comando `ch57x-deck` |
| `assets/ch57x-deck.svg` | Ícono de la app (paleta de `theme.py`) |
| `assets/ch57x-deck.desktop` | Acceso directo para el menú de aplicaciones |
| `install.sh` | Instalación/desinstalación en un paso (`--uninstall`) |
| `packaging/ch57x-deck-uninstall` | Desinstalación autocontenida, invocada por `install.sh --uninstall` |
