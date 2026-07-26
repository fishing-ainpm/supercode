# Exemplos de uso

## Uso básico

```bash
cd meu-projeto/
supercode "adicione autenticação nesse projeto"
```

Saída esperada (resumida):

```
SuperCode — analisando o projeto em /home/user/meu-projeto

▶ PLANEJAMENTO
[planner] 1. Adicionar middleware de autenticação JWT em src/auth.py
           2. Proteger as rotas em src/routes.py
           3. Adicionar variável JWT_SECRET no .env.example
           4. Escrever testes em tests/test_auth.py

=== PLANO PROPOSTO ===
1. Adicionar middleware de autenticação JWT em src/auth.py
...

Aplicar este plano? [y/N] y

▶ IMPLEMENTAÇÃO
  ⚙ [implementer] write_file({'path': 'src/auth.py', ...})
  ⚙ [implementer] edit_file({'path': 'src/routes.py', ...})
[implementer] Criei src/auth.py e protegi 3 rotas em src/routes.py.

▶ REVISÃO
[reviewer] Encontrei o secret JWT hardcoded — corrigido pra ler de env var.

▶ TESTES
  ⚙ [tester] run_command({'command': 'pytest tests/test_auth.py'})
Rodar `pytest tests/test_auth.py`? [y/N] y
[tester] 4 testes passaram.

=== RESUMO FINAL ===
...
```

## Rodar sem nenhuma confirmação (CI, scripts)

```bash
supercode "atualize as dependências do package.json" --yes
```

Use com cuidado: `--yes` também pula a confirmação de `run_command`.

## Especificar o projeto (fora do diretório atual)

```bash
supercode "adicione um endpoint /health" --project ~/projetos/api-service
```

## Misturar provedores por agente

```bash
supercode "refatore o módulo de pagamentos" \
  --planner-provider anthropic \
  --implementer-provider openai --implementer-model gpt-5-codex \
  --reviewer-provider anthropic \
  --tester-provider openai
```

## Histórico de tarefas

Cada projeto guarda seu histórico em `.supercode/session.json`. Tarefas
futuras no mesmo projeto recebem automaticamente um resumo das
tarefas anteriores como contexto pro planner.
