# Supercode

SuperCode é um CLI que orquestra múltiplos agentes de IA especializados — planejamento, implementação, revisão e testes — pra automatizar tarefas de programação de ponta a ponta. Em vez de depender de uma única ferramenta, ele une as capacidades do Claude Code e do Codex CLI num só fluxo: você descreve a tarefa, o SuperCode lê o projeto, propõe um plano, pede sua confirmação, implementa as mudanças, revisa o próprio código em busca de bugs e vulnerabilidades, roda os testes, e te entrega um resumo com o diff. Funciona com qualquer provedor de LLM (Anthropic, OpenAI, DeepSeek, e outros via configuração), com permissões e checkpoints de git em cada etapa

## Instalação Rápida

### Opção 1: One-line install (Recomendado)

```bash
curl -fsSL https://raw.githubusercontent.com/fishing-ainpm/supercode/master/install.sh | bash
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

** R.I.P Donut-corp, foi bom enquanto durou **


## Licença

MIT
