#!/bin/sh
# Installs CH57x Deck: the app itself (via pip, user-level) plus its icon,
# application menu entry and (optionally) the udev rule for USB access
# without root.
#
# From a checkout:
#   ./install.sh              install everything
#   ./install.sh --uninstall  remove everything
#
# Straight from the internet (downloads the project first, then runs this):
#   curl -fsSL https://raw.githubusercontent.com/PericlesSavio/ch57x_deck/main/install.sh | sh
#
# Run as a regular user; sudo is used only for the udev rule.
set -e

REPO="PericlesSavio/ch57x_deck"
BRANCH="main"

# Directory holding this script — resolves to the cwd when piped (`curl | sh`).
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || true)

# No checkout next to the script (piped install): fetch the project into a temp
# dir and re-run the bundled install.sh from there. Non-editable pip install
# means the temp copy is disposable once installed.
if [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/pyproject.toml" ] \
	|| [ ! -f "$SCRIPT_DIR/macropad/__main__.py" ]; then
	echo "==> Downloading CH57x Deck ($REPO, branch $BRANCH)"
	for cmd in curl tar; do
		command -v "$cmd" >/dev/null || { echo "error: $cmd is required" >&2; exit 1; }
	done
	TMP=$(mktemp -d)
	trap 'rm -rf "$TMP"' EXIT
	curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH" \
		| tar -xz -C "$TMP" --strip-components=1
	sh "$TMP/install.sh" "$@"
	exit $?
fi

cd "$SCRIPT_DIR"

if [ "$(id -u)" = 0 ]; then
	SUDO=""
else
	SUDO="sudo"
fi

DESKTOP_ID=ch57x-deck
ICON="$HOME/.local/share/icons/hicolor/scalable/apps/$DESKTOP_ID.svg"
DESKTOP="$HOME/.local/share/applications/$DESKTOP_ID.desktop"
UDEV_RULE=/etc/udev/rules.d/70-macropad-ch57x.rules

if [ "$1" = "--uninstall" ]; then
	exec sh packaging/ch57x-deck-uninstall
fi

echo "==> Checking dependencies"
if ! command -v python3 >/dev/null; then
	echo "error: Python 3.10+ is required" >&2
	exit 1
fi
if ! python3 -m pip --version >/dev/null 2>&1; then
	echo "error: pip is required (the 'python3-pip' package on most distros)" >&2
	exit 1
fi

echo "==> Installing CH57x Deck (pip, user-level, no root)"
# Not editable: the package is copied into the user site, so the install no
# longer depends on this checkout staying in place. (Use 'pip install --user
# -e .' by hand for a development install that tracks the source tree.)
python3 -m pip install --user .

echo "==> Installing the icon and application menu entry"
install -Dm644 assets/ch57x-deck.svg "$ICON"
install -Dm644 assets/ch57x-deck.desktop "$DESKTOP"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
gtk-update-icon-cache -q "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

if ! command -v ch57x-keyboard-tool >/dev/null; then
	echo
	echo "Note: ch57x-keyboard-tool isn't on your PATH. CH57x Deck offers to"
	echo "download it automatically the first time you need it."
fi

# USB access needs a udev rule (root); ask when interactive, otherwise hint.
if [ -f "$UDEV_RULE" ]; then
	: # already installed
elif [ -t 0 ]; then
	printf "Install the udev rule for USB access without root? [Y/n] "
	read -r answer
	case "$answer" in
	[nN]*) echo "Skipped. CH57x Deck can also install it later from within the app." ;;
	*)
		$SUDO install -Dm644 udev/70-macropad-ch57x.rules "$UDEV_RULE"
		$SUDO udevadm control --reload-rules
		$SUDO udevadm trigger
		;;
	esac
else
	echo "Tip: install the udev rule with:"
	echo "  sudo cp udev/70-macropad-ch57x.rules /etc/udev/rules.d/"
	echo "  sudo udevadm control --reload-rules && sudo udevadm trigger"
fi

echo
echo "Done! You can now:"
echo "  - run 'ch57x-deck' in the terminal"
echo "  - open \"CH57x Deck\" in the application menu"
