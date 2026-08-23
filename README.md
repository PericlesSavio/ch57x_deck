English | [Português](README.pt-BR.md) | [Español](README.es.md)

# CH57x Deck

**Graphical frontend (Qt/PySide6) for
[ch57x-keyboard-tool](https://github.com/kriomant/ch57x-keyboard-tool)** —
CH57x Deck doesn't talk to the macropad directly; it builds the configuration
in a visual interface and delegates all USB communication (validation and
writing) to that command-line binary, calling it as a subprocess. Without
ch57x-keyboard-tool installed, the app runs but can't write anything (that's
why it offers to install it automatically — see "Requirements").

Used to configure macropads based on the CH57x chip (USB VID `1189`, PIDs
`8840`/`8842`/`8890` — the generic 3/6/9/12/15-key models with knobs).
Writing happens **on the device firmware**: once uploaded, the mapping works
on any computer, without needing this app or a running daemon.

## Hardware

![Tested macropad](assets/macropad-hardware.png)

The pictured unit is a generic RGB CH57x macropad with two knobs and a
detachable USB cable — this kind of device, sold under many different
brand names, is what CH57x Deck targets.

### Supported models

The **Model** menu switches the interface layout between the generic CH57x
variants:

| Model | Grid | Knobs | Status |
| --- | --- | --- | --- |
| 3 keys + 1 knob | 1 × 3 | 1 | ⚠ untested |
| 6 keys + 1 knob | 2 × 3 | 1 | ⚠ untested |
| 9 keys + 1 knob | 3 × 3 | 1 | ⚠ untested |
| **12 keys + 2 knobs** | **3 × 4** | **2** | **✅ tested** |
| 15 keys + 2 knobs | 3 × 5 | 2 | ⚠ untested |

> **Note:** so far only the **12-key + 2-knob** model has been tested on real
> hardware — it is the default when the app opens. The other variants already
> have a working frontend but are **untested**; each one's rows × columns
> arrangement is assumed. If a preset doesn't match your device, adjust rows,
> columns and knob count by hand in **Model → Custom…**. Reports from anyone
> who tries the other models are welcome.

## Requirements

- Linux with systemd/udev (Fedora, Ubuntu/Debian, Arch, openSUSE…)
- Python 3.10+
- PySide6 installed via pip needs **glibc ≥ 2.34** (its wheel bundles Qt
  itself, statically tied to that floor). Satisfied by current releases —
  Fedora 35+, Ubuntu 22.04+, Debian 12+, RHEL/Rocky/Alma 9+, Arch, openSUSE
  Tumbleweed. On older LTS releases still in use (Ubuntu 20.04, Debian 11,
  RHEL/Rocky/Alma 8), install PySide6 from the distro's own package
  instead — e.g. `apt install python3-pyside6.qtwidgets`, `dnf install
  python3-pyside6`, `pacman -S pyside6` — then install CH57x Deck normally;
  it'll detect and reuse that copy instead of pulling the pip wheel.
- `ch57x-keyboard-tool`: if it's not on the PATH, the app itself offers to
  download the official release on first run (into
  `~/.local/share/ch57x_deck/bin`). The download is **checked by SHA-256**
  against an embedded hash before running — it never executes an unverified
  binary. Under **Help → Update ch57x-keyboard-tool…** you can see the
  installed version, (re)install the verified stable version and check GitHub
  for a newer stable release.

## Installation

```bash
./install.sh
```

Installs the app (pip, user-level, no root), the icon and application menu
entry, and — asking first — the udev rule for USB access without root. Run
as a regular user; `sudo` is only used for that last, optional step. To
remove everything it installed:

```bash
./install.sh --uninstall
```

(interactively asks before deleting your saved configuration; everything
else is removed unconditionally).

### Manual install

If you'd rather do it by hand, or just want the `ch57x-deck` command
without desktop integration:

```bash
pip install --user .
```

This installs the dependencies (PySide6, PyYAML) and creates the
`ch57x-deck` command in `~/.local/bin` (needs to be on `PATH`, which is the
default on most distros). Since it isn't editable, the install isn't tied to
this directory — you can delete the clone afterwards. For development, use
`pip install --user -e .`: `-e` makes the package "editable", so changes to
files under `macropad/` take effect immediately, no reinstall needed.

<details>
<summary>Icon, menu entry and USB permission, by hand</summary>

```bash
# Icon and application menu shortcut
cp assets/ch57x-deck.svg ~/.local/share/icons/hicolor/scalable/apps/
cp assets/ch57x-deck.desktop ~/.local/share/applications/
gtk-update-icon-cache ~/.local/share/icons/hicolor 2>/dev/null
update-desktop-database ~/.local/share/applications 2>/dev/null

# USB permission (root, one-time)
sudo cp udev/70-macropad-ch57x.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

The app also offers to install the udev rule itself, via `pkexec`, if it
detects the macropad without permission.

</details>

## Usage

```bash
ch57x-deck
```

Without installing (e.g. just to try it out), you can also run it directly
from the repository with `python run.py`.

1. Pick the **layer** (the macropad has 3, switched with the side button).
2. Click a **key or knob function** on the grid.
3. Build the action in the editor:
   - **Keyboard** — modifiers + key; up to 5 chained steps (macro). The
     physical layout of the visual keyboard (ABNT2, AZERTY, QWERTZ…) is
     picked in the **Keyboard** menu — a key always records the physical
     position (HID); it's your operating system's layout that decides the
     final character.
   - **Media** — play/pause, volume, etc. (the firmware doesn't allow
     modifiers together with media keys).
   - **Advanced** — free-form expression: mouse (`click(left)`,
     `wheel(-1)`), raw code (`<110>`), manual macros (`ctrl-c,ctrl-v`).
4. **Validate** checks the YAML; **Send to macropad** writes it to firmware.

The last uploaded configuration is kept at
`~/.config/ch57x_deck/current.yaml` (and reloaded when the app opens).
`File → Save/Open` exports and imports YAML compatible with plain
`ch57x-keyboard-tool`.

## Future plans

- **Confirm the 3/6/9/15-key variants on real hardware.** The interface
  already rebuilds the grid and offers the **Model** menu (geometry isn't
  detectable over USB), but only the 12-key + 2-knob model has been tested —
  see "Supported models". The same applies to keyboard layouts beyond ABNT2
  (**Keyboard** menu): they follow each layout's standard mapping but haven't
  been verified.
- **Named profiles.** Today there's only one autosaved configuration
  (`current.yaml`); `File → Save/Open` covers manual import/export, but not
  quickly switching between profiles (e.g. "Work" vs. "Gaming") from the
  menu.
- **Distro packaging** (`.deb`/`.rpm`/PKGBUILD or Flatpak), beyond the
  from-source `install.sh` that already exists.

### Known limitation (not currently possible)

**Reading the mapping already written to the macropad.**
`ch57x-keyboard-tool` only exposes `upload` (write), not a read command —
there's no way to "import" what's already on the device, only rebuild it
from a locally saved YAML.

## Structure

| File | Role |
| --- | --- |
| `macropad/model.py` | In-memory config + YAML (de)serialization |
| `macropad/keys.py` | Catalog of the firmware's keys/modifiers |
| `macropad/backend.py` | Calls ch57x-keyboard-tool; detects USB via sysfs |
| `macropad/tool_manager.py` | Install/update dialog for the binary (verifies SHA-256) |
| `macropad/action_editor.py` | Widget for editing one action |
| `macropad/keyboard_widget.py` | Clickable visual keyboard |
| `macropad/layouts.py` | Physical keyboard layouts (ABNT2, AZERTY…) |
| `macropad/test_area.py` | Test area (captures what the pad sends) |
| `macropad/main_window.py` | Main window |
| `macropad/i18n.py` | Translations (pt-BR, en, es) |
| `macropad/settings.py` | Persistent preferences |
| `macropad/theme.py` | Monokai + light theme; follows the system theme |
| `tests/` | Pure-logic tests (pytest, no hardware or Qt) |
| `udev/70-macropad-ch57x.rules` | USB permission rule |
| `pyproject.toml` | Packaging; generates the `ch57x-deck` command |
| `assets/ch57x-deck.svg` | App icon (matches `theme.py`'s palette) |
| `assets/ch57x-deck.desktop` | Application menu shortcut |
| `install.sh` | One-step install/uninstall (`--uninstall`) |
| `packaging/ch57x-deck-uninstall` | Self-contained uninstall, run by `install.sh --uninstall` |
| `scripts/pin_release.py` | Maintenance: pins the SHA-256 of a new stable binary release |
| `LICENSE` | GPL-3.0 text |

## Tests

The tests cover the pure logic (model/YAML, keys, layouts, translations,
theme) — no hardware or GUI:

```bash
pip install --user '.[dev]'   # installs pytest
pytest
```

## License

[GPL-3.0-or-later](LICENSE). CH57x Deck talks to the macropad **only**
through `ch57x-keyboard-tool`, invoking it as a subprocess (without linking
its code), so this license choice imposes nothing on that separate project.
