# SPDX-License-Identifier: GPL-3.0-or-later
"""Comunicação com o macropad via ch57x-keyboard-tool.

O binário é procurado no PATH e em diretórios XDG; se não existir, pode ser
baixado da release oficial no GitHub para ~/.local/share/ch57x_deck/bin.
Nada aqui depende de distro específica.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import tarfile
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

TOOL_NAME = "ch57x-keyboard-tool"
TOOL_REPO = "kriomant/ch57x-keyboard-tool"

_RELEASE_TARGETS = {
    "x86_64": "x86_64-unknown-linux-gnu",
    "aarch64": "aarch64-unknown-linux-gnu",
}

# Release estável verificado: SHA-256 do .tar.gz oficial de cada alvo, conferido
# à mão contra github.com/kriomant/ch57x-keyboard-tool/releases. Instalar só
# executa um binário cujo hash bate com um destes — nunca um download às cegas.
# Ao sair uma nova estável: baixe os .tar.gz, rode `sha256sum`, atualize os
# hashes abaixo e o LATEST_KNOWN.
KNOWN_RELEASES: dict[str, dict[str, str]] = {
    "v1.7.0": {
        "x86_64-unknown-linux-gnu": "83bd23cc4c84303ce35aa1c981e305b8cf885ef534397369e97883b2c93214b4",
        "aarch64-unknown-linux-gnu": "565958f1732d064905a96bc1b0daabd03f7e5baf1fcca76f834bc2b3efe266ab",
    },
}

# Versão estável que o app instala e mantém.
LATEST_KNOWN = "v1.7.0"

# VID (0x1189) e PIDs dos macropads CH57x conhecidos.
DEVICE_VID = "1189"
DEVICE_PIDS = ("8840", "8842", "8890")

# Regra udev que dá acesso ao usuário logado (tag processada pela
# 73-seat-late.rules do systemd — por isso o prefixo precisa ser < 73).
UDEV_RULE_PATH = "/etc/udev/rules.d/70-macropad-ch57x.rules"
OLD_UDEV_RULE_PATH = "/etc/udev/rules.d/99-macropad-ch57x.rules"
UDEV_RULE_CONTENT = "".join(
    f'SUBSYSTEM=="usb", ATTRS{{idVendor}}=="{DEVICE_VID}", '
    f'ATTRS{{idProduct}}=="{pid}", TAG+="uaccess"\n'
    for pid in DEVICE_PIDS
)


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return Path(base) / "ch57x_deck"


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(base) / "ch57x_deck"


@dataclass
class CommandResult:
    ok: bool
    stdout: str
    stderr: str

    @property
    def message(self) -> str:
        return (self.stderr or self.stdout).strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _extract_member(tar: tarfile.TarFile, member: tarfile.TarInfo, dest_dir: Path) -> None:
    """Extrai um membro usando o filtro 'data' quando disponível.

    O parâmetro `filter` só existe no Python 3.12+ (e nos patches recentes do
    3.9–3.11); em versões anteriores cai no comportamento clássico. O membro é
    um único arquivo regular com nome fixo, então não há risco de traversal.
    """
    try:
        tar.extract(member, dest_dir, filter="data")
    except TypeError:
        tar.extract(member, dest_dir)


class Backend:
    """Envolve o ch57x-keyboard-tool em chamadas de alto nível."""

    def __init__(self) -> None:
        self._tool: str | None = None

    # ------------------------------------------------------------------
    # Localização / instalação do binário
    # ------------------------------------------------------------------

    def find_tool(self) -> str | None:
        """Procura o binário no PATH e no diretório de dados do app."""
        if self._tool and Path(self._tool).exists():
            return self._tool

        found = shutil.which(TOOL_NAME)
        if not found:
            bundled = data_dir() / "bin" / TOOL_NAME
            if bundled.exists() and os.access(bundled, os.X_OK):
                found = str(bundled)

        self._tool = found
        return found

    def target(self) -> str | None:
        """Alvo de release para a arquitetura atual (None se não houver)."""
        return _RELEASE_TARGETS.get(platform.machine())

    def download_url(self, version: str = LATEST_KNOWN) -> str | None:
        tgt = self.target()
        if not tgt:
            return None
        return (
            f"https://github.com/{TOOL_REPO}/releases/download/"
            f"{version}/{TOOL_NAME}-{tgt}.tar.gz"
        )

    def pinned_sha256(self, version: str) -> str | None:
        """SHA-256 verificado da versão para esta arquitetura (None se não pinado)."""
        tgt = self.target()
        if not tgt:
            return None
        return KNOWN_RELEASES.get(version, {}).get(tgt)

    def known_versions(self) -> list[str]:
        """Versões verificadas disponíveis nesta arquitetura, mais nova primeiro."""
        tgt = self.target()

        def order(tag: str) -> tuple[int, ...]:
            return tuple(int(p) for p in tag.lstrip("v").split("."))

        versions = [v for v, h in KNOWN_RELEASES.items() if not tgt or tgt in h]
        return sorted(versions, key=order, reverse=True)

    def installed_version(self) -> str | None:
        """Versão do binário instalado (via `--version`), no formato 'vX.Y.Z'."""
        tool = self.find_tool()
        if not tool:
            return None
        try:
            proc = subprocess.run(
                [tool, "--version"], capture_output=True, text=True, timeout=5
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        match = re.search(r"(\d+\.\d+\.\d+)", f"{proc.stdout}\n{proc.stderr}")
        return f"v{match.group(1)}" if match else None

    def latest_online(self) -> str | None:
        """Tag da última release no GitHub (None se offline ou indisponível)."""
        url = f"https://api.github.com/repos/{TOOL_REPO}/releases/latest"
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/vnd.github+json", "User-Agent": TOOL_NAME},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.load(resp)
        except (OSError, ValueError):
            return None
        tag = data.get("tag_name")
        return tag if isinstance(tag, str) else None

    def fetch_release(self, version: str) -> tuple[Path, str]:
        """Baixa o .tar.gz da versão para um diretório temporário.

        Devolve (caminho, sha256_hex). Levanta RuntimeError em erro de rede ou
        arquitetura sem release. Quem chama decide se o hash é aceitável e então
        chama `install_from()`; se desistir, deve remover `caminho.parent`.
        """
        url = self.download_url(version)
        if not url:
            raise RuntimeError(
                f"Arquitetura sem release pronta: {platform.machine()}. "
                f"Instale o {TOOL_NAME} manualmente (cargo install {TOOL_NAME})."
            )
        tmp_dir = Path(tempfile.mkdtemp(prefix="ch57x_deck_dl_"))
        archive = tmp_dir / f"{TOOL_NAME}-{version}.tar.gz"
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                archive.write_bytes(resp.read())
        except OSError as exc:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise RuntimeError(f"Falha ao baixar {url}: {exc}") from exc
        return archive, _sha256(archive)

    def install_from(self, archive: Path) -> str:
        """Extrai o binário de um .tar.gz já baixado e o torna executável.

        A verificação de integridade é responsabilidade de quem baixou (ver
        `install_tool`). Remove o diretório temporário do arquivo ao final.
        """
        dest_dir = data_dir() / "bin"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / TOOL_NAME
        try:
            with tarfile.open(archive) as tar:
                member = next(
                    (m for m in tar.getmembers() if Path(m.name).name == TOOL_NAME),
                    None,
                )
                if member is None:
                    raise RuntimeError("Binário não encontrado dentro do arquivo baixado.")
                member.name = TOOL_NAME
                _extract_member(tar, member, dest_dir)
        finally:
            shutil.rmtree(archive.parent, ignore_errors=True)
        dest.chmod(0o755)
        self._tool = str(dest)
        return self._tool

    def install_tool(self, version: str = LATEST_KNOWN) -> str:
        """Baixa, CONFERE o SHA-256 contra o hash pinado e instala.

        Só para versões conhecidas (hash embutido). Levanta RuntimeError se não
        houver hash pinado ou se o download não bater — este caminho nunca
        executa um binário não verificado.
        """
        pinned = self.pinned_sha256(version)
        if pinned is None:
            raise RuntimeError(
                f"{version} não tem hash verificado para esta arquitetura; "
                "instalação abortada."
            )
        archive, digest = self.fetch_release(version)
        if digest != pinned:
            shutil.rmtree(archive.parent, ignore_errors=True)
            raise RuntimeError(
                f"O arquivo baixado de {version} não confere com o hash "
                "verificado. Instalação abortada por segurança."
            )
        return self.install_from(archive)

    # ------------------------------------------------------------------
    # Dispositivo
    # ------------------------------------------------------------------

    def _device_sysfs(self) -> Path | None:
        """Diretório sysfs do macropad, se conectado."""
        usb_root = Path("/sys/bus/usb/devices")
        if not usb_root.is_dir():
            return None
        for device in usb_root.iterdir():
            vid_file = device / "idVendor"
            pid_file = device / "idProduct"
            try:
                if not vid_file.is_file():
                    continue
                vid = vid_file.read_text().strip()
                pid = pid_file.read_text().strip()
            except OSError:
                continue
            if vid == DEVICE_VID and pid in DEVICE_PIDS:
                return device
        return None

    def device_present(self) -> bool:
        """Confere no sysfs se algum macropad CH57x está conectado."""
        return self._device_sysfs() is not None

    def device_node(self) -> Path | None:
        """Nó em /dev/bus/usb que o ch57x-keyboard-tool precisa abrir."""
        sysfs = self._device_sysfs()
        if not sysfs:
            return None
        try:
            bus = int((sysfs / "busnum").read_text())
            dev = int((sysfs / "devnum").read_text())
        except (OSError, ValueError):
            return None
        return Path(f"/dev/bus/usb/{bus:03d}/{dev:03d}")

    def device_accessible(self) -> bool:
        """True se o usuário atual já pode gravar no macropad (ACL/permissão)."""
        node = self.device_node()
        return bool(node) and os.access(node, os.R_OK | os.W_OK)

    def udev_rule_installed(self) -> bool:
        return Path(UDEV_RULE_PATH).is_file()

    def can_install_udev_rule(self) -> bool:
        return shutil.which("pkexec") is not None

    def install_udev_rule(self) -> CommandResult:
        """Instala a regra udev via pkexec (senha pedida pelo polkit gráfico).

        Também remove a regra 99-* antiga (ineficaz) e recarrega o udev, de
        modo que o acesso passa a valer sem reconectar o dispositivo.
        """
        pkexec = shutil.which("pkexec")
        if not pkexec:
            return CommandResult(False, "", "pkexec não encontrado")

        with tempfile.NamedTemporaryFile(
            "w", suffix=".rules", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(UDEV_RULE_CONTENT)
            tmp = handle.name

        script = (
            f"install -m 0644 {shlex.quote(tmp)} {shlex.quote(UDEV_RULE_PATH)}"
            f" && rm -f {shlex.quote(OLD_UDEV_RULE_PATH)}"
            " && udevadm control --reload-rules && udevadm trigger"
        )
        try:
            proc = subprocess.run(
                [pkexec, "sh", "-c", script],
                capture_output=True,
                text=True,
                timeout=180,  # tempo para o usuário digitar a senha
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return CommandResult(False, "", str(exc))
        finally:
            os.unlink(tmp)
        return CommandResult(proc.returncode == 0, proc.stdout, proc.stderr)

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    def _run(self, args: list[str], stdin_text: str | None = None) -> CommandResult:
        tool = self.find_tool()
        if not tool:
            return CommandResult(False, "", f"{TOOL_NAME} não encontrado.")
        try:
            proc = subprocess.run(
                [tool, *args],
                input=stdin_text,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return CommandResult(False, "", str(exc))
        return CommandResult(proc.returncode == 0, proc.stdout, proc.stderr)

    def validate(self, yaml_text: str) -> CommandResult:
        return self._run(["validate"], stdin_text=yaml_text)

    def upload(self, yaml_text: str) -> CommandResult:
        return self._run(["upload"], stdin_text=yaml_text)
