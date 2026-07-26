# Supercode

Descrição do seu projeto aqui.

## Instalação Rápida

### Opção 1: One-line install (Recomendado)

```bash
curl https://raw.githubusercontent.com/fishing-ainpm/supercode/master/install.sh | bash
```

Depois atualize seu shell:
```bash
source ~/.bashrc  # ou source ~/.zshrc para zsh
```

### Opção 2: Instalação Manual

```bash
# Clone o repositório
git clone https://github.com/fishing-ainpm/supercode.git
cd supercode

# Crie um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Instale o projeto
pip install -e .
```

## Uso

```bash
supercode --help
```

## Requisitos

- Python 3.8+
- Git

## Dependências

Veja `requirements.txt` para a lista completa de dependências.

## Desenvolvimento

Para contribuir ao projeto:

```bash
# Clone o repositório
git clone https://github.com/fishing-ainpm/supercode.git
cd supercode

# Crie um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale em modo desenvolvimento
pip install -e .
pip install -r requirements-dev.txt  # se existir
```

## Licença

MIT
