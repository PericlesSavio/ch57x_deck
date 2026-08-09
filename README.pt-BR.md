[English](README.md) | Português | [Español](README.es.md)

# CH57x Deck

**Frontend gráfico (Qt/PySide6) para o
[ch57x-keyboard-tool](https://github.com/kriomant/ch57x-keyboard-tool)** — o
CH57x Deck não fala com o macropad diretamente; ele monta a configuração numa
interface visual e delega toda a comunicação USB (validação e gravação) para
esse binário de linha de comando, chamando-o como subprocesso. Sem o
ch57x-keyboard-tool instalado, o app roda mas não consegue gravar nada (por
isso ele oferece instalá-lo automaticamente — veja "Requisitos").

Serve para configurar macropads baseados no chip CH57x (VID USB `1189`,
PIDs `8840`/`8842`/`8890` — os modelos genéricos de 3/6/9/12/15 teclas com
knobs). A gravação é feita **no firmware do dispositivo**: depois de enviar,
o mapeamento funciona em qualquer computador, sem precisar deste app nem de
um daemon rodando.

## Hardware

![Macropad testado](assets/macropad-hardware.png)

A unidade da foto é um macropad CH57x genérico com RGB, dois knobs e cabo
USB destacável — esse tipo de dispositivo, vendido sob várias marcas
diferentes, é o alvo do CH57x Deck.

## Requisitos

- Linux com systemd/udev (Fedora, Ubuntu/Debian, Arch, openSUSE…)
- Python 3.10+
- `ch57x-keyboard-tool`: se não estiver no PATH, o próprio app oferece
  baixar a release oficial na primeira execução (para
  `~/.local/share/ch57x_deck/bin`)

## Instalação

```bash
./install.sh
```

Instala o app (pip, nível de usuário, sem root), o ícone e o atalho no menu
de aplicativos e — perguntando antes — a regra udev para acesso USB sem
root. Roda como usuário comum; o `sudo` só é usado nesse último passo,
opcional. Para remover tudo que foi instalado:

```bash
./install.sh --uninstall
```

(pergunta antes de apagar sua configuração salva; o resto é removido sem
perguntar).

### Instalação manual

Se preferir fazer na mão, ou só quiser o comando `ch57x-deck` sem a
integração com o desktop:

```bash
pip install --user -e .
```

Isso instala as dependências (PySide6, PyYAML) e cria o comando `ch57x-deck`
em `~/.local/bin` (precisa estar no `PATH`, o que já é o padrão na maioria
das distros). `-e` deixa o pacote "editável": alterações nos arquivos em
`macropad/` valem na hora, sem reinstalar — útil durante desenvolvimento; para
um uso puramente final tanto faz usar `-e` ou não.

<details>
<summary>Ícone, atalho de menu e permissão USB, na mão</summary>

```bash
# Ícone e atalho no menu de aplicativos
cp assets/ch57x-deck.svg ~/.local/share/icons/hicolor/scalable/apps/
cp assets/ch57x-deck.desktop ~/.local/share/applications/
gtk-update-icon-cache ~/.local/share/icons/hicolor 2>/dev/null
update-desktop-database ~/.local/share/applications 2>/dev/null

# Permissão USB (root, uma vez só)
sudo cp udev/70-macropad-ch57x.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

O app também oferece instalar a regra udev sozinho, via `pkexec`, se
detectar o macropad sem permissão.

</details>

## Uso

```bash
ch57x-deck
```

Sem instalar (ex.: só para testar), também dá para rodar direto do
repositório com `python run.py`.

1. Escolha a **camada** (o macropad tem 3, alternadas pelo botão lateral).
2. Clique numa **tecla ou função de knob** na grade.
3. Monte a ação no editor:
   - **Teclado** — modificadores + tecla; até 5 passos encadeados (macro).
   - **Mídia** — play/pause, volume etc. (o firmware não permite
     modificadores junto com mídia).
   - **Avançado** — expressão livre: mouse (`click(left)`, `wheel(-1)`),
     código bruto (`<110>`), macros manuais (`ctrl-c,ctrl-v`).
4. **Validar** confere o YAML; **Enviar ao macropad** grava no firmware.

A última configuração enviada fica em `~/.config/ch57x_deck/current.yaml`
(e é recarregada ao abrir o app). `Arquivo → Salvar/Abrir` exporta e importa
YAML compatível com o `ch57x-keyboard-tool` puro.

## Planos futuros

- **Suporte às variantes de 3/6/9/15 teclas e 0–3 knobs.** O backend
  (ch57x-keyboard-tool) e o modelo YAML já aceitam qualquer geometria; falta a
  interface reconstruir a grade quando a geometria muda e oferecer um menu
  "Modelo do macropad" (a geometria não é detectável via USB). Hoje a UI
  assume 3×4 + 2 knobs e abrir um YAML de outra geometria quebra
  (`IndexError` em `_refresh_pad_labels`).
- **Testes automatizados** (pytest) para `model.py` (serialização YAML) e
  `keys.py` (validação de ações) — hoje a verificação é toda manual.
- **Perfis nomeados.** Hoje só existe uma configuração autosalva
  (`current.yaml`); `Arquivo → Salvar/Abrir` cobre import/export manual, mas
  não uma troca rápida entre perfis (ex.: "Trabalho" vs. "Jogo") direto no
  menu.
- **Escolher uma licença** antes de publicar o repositório publicamente —
  ainda não definida.

### Limitação conhecida (não é possível hoje)

**Ler o mapeamento já gravado no macropad.** O `ch57x-keyboard-tool` só
expõe `upload` (gravar), não um comando de leitura — não dá para "importar"
o que já está no dispositivo, só reconstruir a partir de um YAML salvo
localmente.

## Estrutura

| Arquivo | Papel |
| --- | --- |
| `macropad/model.py` | Config em memória + (de)serialização YAML |
| `macropad/keys.py` | Catálogo de teclas/modificadores do firmware |
| `macropad/backend.py` | Chama o ch57x-keyboard-tool; detecta USB via sysfs |
| `macropad/action_editor.py` | Widget de edição de uma ação |
| `macropad/keyboard_widget.py` | Teclado visual clicável |
| `macropad/test_area.py` | Área de teste (captura o que o pad envia) |
| `macropad/main_window.py` | Janela principal |
| `macropad/i18n.py` | Traduções (pt-BR, en, es) |
| `macropad/settings.py` | Preferências persistentes |
| `macropad/theme.py` | Tema Monokai (cinza escuro, cantos retos) |
| `udev/70-macropad-ch57x.rules` | Regra de permissão USB |
| `pyproject.toml` | Empacotamento; gera o comando `ch57x-deck` |
| `assets/ch57x-deck.svg` | Ícone do app (paleta do `theme.py`) |
| `assets/ch57x-deck.desktop` | Atalho para o menu de aplicativos |
| `install.sh` | Instalação/remoção num passo só (`--uninstall`) |
| `packaging/ch57x-deck-uninstall` | Desinstalação autocontida, chamada por `install.sh --uninstall` |
