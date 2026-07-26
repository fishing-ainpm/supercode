# Instalação

Requer Python 3.11+.

## Via pip (modo editável, recomendado durante desenvolvimento)

```bash
git clone https://github.com/donut-corp/supercode.git
cd supercode
pip install -e . --break-system-packages   # a flag só é necessária no Termux/Debian
```

Isso registra o comando `supercode` no seu PATH (via entry_point do
`pyproject.toml`).

## Testando a instalação

```bash
supercode --help
```

## No Termux (aarch64)

O SuperCode não tem nenhuma dependência nativa — só `requests` — então
roda direto no Termux sem precisar do Debian via proot-distro. Ainda
assim, se você já usa o Debian pra outras ferramentas (Claude Code,
claw-code), rodar o SuperCode lá também funciona sem alterações.

```bash
pkg install python
pip install -e . --break-system-packages
```

## Verificando dependências

```bash
python3 -c "import requests; print('ok')"
```
