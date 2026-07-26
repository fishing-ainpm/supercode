# Configuração das APIs

O SuperCode precisa de pelo menos uma API key configurada (Anthropic
e/ou OpenAI/DeepSeek). Cada um dos 4 agentes (planner, implementer,
reviewer, tester) pode usar um provedor **diferente** — assim dá pra,
por exemplo, usar Claude pro planejamento/revisão e Codex pra
implementação, como no exemplo do enunciado.

## Opção 1 — Variáveis de ambiente (mais simples)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export DEEPSEEK_API_KEY="sk-..."   # se for usar DeepSeek como provider "openai-compatible"
```

## Opção 2 — Arquivo de config

```bash
supercode init-config
```

Isso cria `~/.config/supercode/config.toml`:

```toml
[anthropic]
api_key = "sk-ant-..."
model = "claude-sonnet-4-6"

[openai]
api_key = "sk-..."
model = "gpt-5-codex"

[deepseek]
api_key = "sk-..."
model = "deepseek-v4-pro"
base_url = "https://api.deepseek.com/v1"
```

Variável de ambiente sempre tem prioridade sobre o arquivo, caso os
dois existam.

## Escolhendo o provedor/modelo por agente

Por padrão: `planner=anthropic`, `implementer=openai`,
`reviewer=anthropic`, `tester=openai`. Pra mudar:

```bash
supercode "adicione autenticação" \
  --planner-provider anthropic --planner-model claude-sonnet-4-6 \
  --implementer-provider deepseek --implementer-model deepseek-v4-pro \
  --reviewer-provider anthropic \
  --tester-provider deepseek
```

## Segurança das chaves

- Nunca commite `config.toml` num repositório público.
- Prefira variáveis de ambiente em CI/CD.
- O SuperCode nunca escreve sua API key em nenhum arquivo do projeto
  ou em `.supercode/session.json`.
