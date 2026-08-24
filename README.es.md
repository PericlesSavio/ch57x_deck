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

### Modelos compatibles

El menú **Modelo** cambia la distribución de la interfaz entre las variantes
genéricas del chip CH57x:

| Modelo | Rejilla | Knobs | Estado |
| --- | --- | --- | --- |
| 3 teclas + 1 knob | 1 × 3 | 1 | ⚠ no probado |
| 6 teclas + 1 knob | 2 × 3 | 1 | ⚠ no probado |
| 9 teclas + 1 knob | 3 × 3 | 1 | ⚠ no probado |
| **12 teclas + 2 knobs** | **3 × 4** | **2** | **✅ probado** |
| 15 teclas + 2 knobs | 3 × 5 | 2 | ⚠ no probado |

> **Aviso:** hasta ahora solo se ha probado el modelo de **12 teclas + 2
> knobs** con hardware real — es el predeterminado al abrir la app. Las demás
> variantes ya tienen el frontend listo, pero **no se han probado**; la
> disposición de filas × columnas de cada una es supuesta. Si el preset no
> coincide con tu dispositivo, ajusta filas, columnas y número de knobs a
> mano en **Modelo → Personalizado…**. Los informes de quienes prueben los
> demás modelos son bienvenidos.

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
  `~/.local/share/ch57x_deck/bin`).

## Instalación

En un comando (descarga el proyecto y lo instala):

```bash
curl -fsSL https://raw.githubusercontent.com/PericlesSavio/ch57x_deck/main/install.sh | sh
```

O, desde un clon del repositorio:

```bash
./install.sh
```

> Ejecutar un script directo de internet corre código remoto sin revisión.
> Si prefiere revisarlo antes, descárguelo: `curl -fsSL .../install.sh -o
> install.sh`, léalo, y luego `sh install.sh`.

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
pip install --user .
```

Esto instala las dependencias (PySide6, PyYAML) y crea el comando
`ch57x-deck` en `~/.local/bin` (debe estar en el `PATH`, lo cual ya es el
predeterminado en la mayoría de las distros). Al no ser editable, la
instalación no queda atada a este directorio — puede borrar el clon después.
Para desarrollo, use `pip install --user -e .`: `-e` deja el paquete
"editable", así los cambios en los archivos de `macropad/` se aplican al
instante, sin reinstalar.

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
     (macro). La distribución física del teclado visual (ABNT2, AZERTY,
     QWERTZ…) se elige en el menú **Teclado** — la tecla siempre graba la
     posición física (HID); es la distribución de su sistema operativo la
     que decide el carácter final.
   - **Multimedia** — reproducir/pausar, volumen, etc. (el firmware no
     permite modificadores junto con teclas multimedia).
   - **Avanzado** — expresión libre: ratón (`click(left)`, `wheel(-1)`),
     código bruto (`<110>`), macros manuales (`ctrl-c,ctrl-v`).
4. **Validar** revisa el YAML; **Enviar al macropad** lo graba en el
   firmware.

El menú **Editar** ayuda al armar: deshacer/rehacer (`Ctrl+Z` / `Ctrl+Shift+Z`),
copiar y pegar la acción de una tecla en otra (`Ctrl+Shift+C` / `Ctrl+Shift+V`)
y **copiar la capa actual** a otra como punto de partida.

El botón **Limpiar tecla** (rojo, en la barra inferior) borra la acción de la
selección, valiendo para las tres pestañas. Al enviar, una tecla vacía se
**desactiva** en el dispositivo — la asignación anterior se sobrescribe.

La última configuración enviada queda en
`~/.config/ch57x_deck/current.yaml` (y se recarga al abrir la app).
`Archivo → Guardar/Abrir` exporta e importa YAML compatible con el
`ch57x-keyboard-tool` puro.

## Novedades

### 0.9.1
- Menú **Editar**: deshacer/rehacer, copiar/pegar la acción entre teclas y
  duplicar una capa.
- **Limpiar tecla** en la barra inferior, valiendo para las tres pestañas; una
  tecla vacía ahora **desactiva** la tecla en el dispositivo al enviar (antes se
  mantenía la asignación anterior).
- Traducciones separadas en [`macropad/locales/`](macropad/locales/) — una por
  idioma, fáciles de traducir.
- Textos estándar de Qt traducidos (Mostrar los detalles…, OK, Cancelar).
- Eliminada la actualización en línea de `ch57x-keyboard-tool`; la app instala la
  versión que ya trae incorporada.

### 0.9.0
- Primera versión: modelos de 3/6/9/12/15 teclas (menú **Modelo**),
  distribuciones de teclado (ABNT2, AZERTY, QWERTZ…), tema claro/oscuro que sigue
  el sistema, atajos de menú, instalador por `curl`, integración con el escritorio
  y licencia GPL-3.0.

## Planes futuros

- **Confirmar las variantes de 3/6/9/15 teclas con hardware real.** La
  interfaz ya reconstruye la grilla y ofrece el menú **Modelo** (la geometría
  no es detectable por USB), pero solo el modelo de 12 teclas + 2 knobs fue
  probado — ver "Modelos compatibles". Lo mismo aplica a las distribuciones de
  teclado más allá del ABNT2 (menú **Teclado**): siguen el mapeo estándar de
  cada distribución, pero no fueron verificadas.
- **Perfiles con nombre.** Hoy solo existe una configuración autoguardada
  (`current.yaml`); `Archivo → Guardar/Abrir` cubre la importación/
  exportación manual, pero no un cambio rápido entre perfiles (ej.:
  "Trabajo" vs. "Juego") directo desde el menú.
- **Empaquetado para las distros** (`.deb`/`.rpm`/PKGBUILD o Flatpak),
  más allá del `install.sh` desde el fuente que ya existe.

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
| `macropad/layouts.py` | Distribuciones físicas del teclado (ABNT2, AZERTY…) |
| `macropad/test_area.py` | Área de prueba (captura lo que envía el pad) |
| `macropad/main_window.py` | Ventana principal |
| `macropad/i18n.py` | Carga las traducciones y elige el idioma |
| `macropad/locales/*.yaml` | Traducciones, una por idioma (pt-BR, en, es) |
| `macropad/settings.py` | Preferencias persistentes |
| `macropad/theme.py` | Tema Monokai + claro; sigue el tema del sistema |
| `tests/` | Pruebas de lógica pura (pytest, sin hardware ni Qt) |
| `udev/70-macropad-ch57x.rules` | Regla de permiso USB |
| `pyproject.toml` | Empaquetado; genera el comando `ch57x-deck` |
| `assets/ch57x-deck.svg` | Ícono de la app (paleta de `theme.py`) |
| `assets/ch57x-deck.desktop` | Acceso directo para el menú de aplicaciones |
| `install.sh` | Instalación/desinstalación en un paso (`--uninstall`) |
| `packaging/ch57x-deck-uninstall` | Desinstalación autocontenida, invocada por `install.sh --uninstall` |
| `LICENSE` | Texto de la GPL-3.0 |

## Traducciones

Cada idioma es un archivo en [`macropad/locales/`](macropad/locales/) — texto
simple que cualquiera puede editar. Para añadir un idioma:

1. Copie `en.yaml` a `<código>.yaml` (ej.: `fr.yaml`, `de.yaml`).
2. Traduzca solo los **valores** a la derecha de los dos puntos — conserve las
   claves, los campos entre `{ }` (ej.: `{version}`) y las marcas HTML.
3. Registre el código en `LANGUAGES`, en [`macropad/i18n.py`](macropad/i18n.py).

Un aporte de traducción (pull request) no necesita más que un editor de texto.

## Pruebas

Las pruebas cubren la lógica pura (modelo/YAML, teclas, distribuciones,
traducciones, tema) — sin hardware ni interfaz gráfica:

```bash
pip install --user '.[dev]'   # instala pytest
pytest
```

## Licencia

[GPL-3.0-or-later](LICENSE). CH57x Deck se comunica con el macropad **solo**
a través de `ch57x-keyboard-tool`, invocándolo como subproceso (sin enlazar
su código), por lo que esta elección de licencia no impone nada a ese
proyecto aparte.
