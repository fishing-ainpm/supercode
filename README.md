# SuperCode

Orquestrador multi-agente de programação: une planejamento, implementação,
revisão e testes num único CLI, sobre qualquer provedor de LLM (Claude,
GPT/Codex, DeepSeek, ou o que vier depois).

```
supercode "adicione autenticação nesse projeto"
```

O SuperCode vai:
1. Ler o projeto e entender a estrutura de arquivos.
2. Mostrar um **plano** antes de tocar em qualquer código.
3. Pedir sua **confirmação**.
4. Implementar as mudanças.
5. Revisar o próprio código em busca de bugs/vulnerabilidades.
6. Rodar (ou escrever e rodar) testes.
7. Mostrar um resumo final + diff via git.

## Por que Python (e não Rust)

O SuperCode é essencialmente **orquestração de I/O**: chamadas de API HTTP
pra múltiplos provedores, leitura/escrita de arquivos, e disparo de
subprocessos — nenhuma dessas partes é CPU-bound. Para esse perfil de
workload, Rust não traria ganho de performance real, mas custaria
muito mais tempo de desenvolvimento (tipagem de JSON de APIs externas,
async, etc) numa área do projeto — a lógica dos agentes e prompts —
que muda com muita frequência durante o desenvolvimento.

Python foi escolhido porque:
- **Iteração rápida**: prompts de agente e schemas de tools mudam o
  tempo todo; recompilar não agrega nada aqui.
- **Ecossistema de API**: `requests`/`httpx` cobrem 100% do necessário
  pra falar com Anthropic e OpenAI sem SDK pesado.
- **stdlib robusta pra shell/git/arquivos** (`subprocess`, `pathlib`).
- Roda igualmente bem dentro do Debian via proot-distro no Termux.

Se no futuro uma parte específica virar gargalo real (ex: parsing de
projetos gigantes, indexação de código pra busca semântica), essa parte
pode virar uma extensão nativa em Rust chamada via `subprocess` ou
`pyo3` — sem reescrever o orquestrador inteiro.

## Instalação

Veja [INSTALL.md](./INSTALL.md).

## Configuração das APIs

Veja [CONFIG.md](./CONFIG.md).

## Uso

Veja [USAGE.md](./USAGE.md).

## Adicionando novos modelos/provedores

Veja [ADDING_MODELS.md](./ADDING_MODELS.md).

## Arquitetura

```
supercode/
├── core/            # config, orquestrador do pipeline
│   ├── config.py
│   └── orchestrator.py
├── agents/          # os 4 agentes especializados + loop de tool-use genérico
│   ├── base.py
│   └── specialized.py
├── providers/        # adaptadores por LLM (Anthropic, OpenAI, DeepSeek...)
│   ├── base.py
│   ├── anthropic_provider.py
│   └── openai_provider.py
├── tools/            # capacidades: arquivo, shell, git
│   ├── file_tools.py
│   ├── shell_tools.py
│   └── git_tools.py
├── memory/           # sessão persistida por projeto (.supercode/session.json)
│   └── session.py
├── cli/              # entrypoint
│   └── main.py
└── docs/
```

### Fluxo de permissões por agente

| Agente       | read_file | write/edit_file | run_command |
|--------------|:---------:|:----------------:|:-----------:|
| Planner      | ✅        | ❌               | ❌          |
| Implementer  | ✅        | ✅               | ✅ (confirma) |
| Reviewer     | ✅        | ✅ (correções)   | ❌          |
| Tester       | ✅        | ✅ (só testes)   | ✅ (confirma) |

`run_command` **sempre** pede confirmação do usuário, a menos que
`--yes` seja passado — essa é a única flag que remove confirmações,
e mesmo assim o plano ainda é exibido antes de qualquer mudança.

### Checkpoints com git

Antes de qualquer implementação, o orquestrador cria um commit de
checkpoint (`git commit --allow-empty`). Se algo der muito errado,
`git reset --hard HEAD` volta pro estado anterior à tarefa.
