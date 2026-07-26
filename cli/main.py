#!/usr/bin/env python3
"""
cli/main.py

Ponto de entrada: `supercode "adicione autenticação nesse projeto"`
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# garante que o pacote do projeto esteja no path para imports relativos funcionarem
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import example_config_toml, resolve_provider_config
from core.orchestrator import Providers, SuperCodeOrchestrator
from providers import build_provider

# import do aquário (módulo que exibe o splash/trigger)
from cli import aquarium

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"


def event_printer(kind: str, text: str) -> None:
    if kind == "stage":
        print(f"\n{BOLD}{CYAN}▶ {text.upper()}{RESET}")
    elif kind == "agent_text":
        print(f"{text}")
    elif kind == "tool_call":
        print(f"{DIM}  ⚙ {text}{RESET}")


def build_providers(args) -> Providers:
    def make(role_provider: str, role_model: str | None):
        cfg = resolve_provider_config(role_provider, role_model)
        kwargs = {"base_url": cfg.base_url} if cfg.base_url else {}
        return build_provider(cfg.provider, cfg.api_key, cfg.model, **kwargs)

    return Providers(
        planner=make(args.planner_provider, args.planner_model),
        implementer=make(args.implementer_provider, args.implementer_model),
        reviewer=make(args.reviewer_provider, args.reviewer_model),
        tester=make(args.tester_provider, args.tester_model),
    )


def cmd_run(args) -> None:
    """Executa a tarefa. Regras especiais relacionadas ao "gatilho" visual:

    - Se o usuário executar `supercode` (sem argumentos) ou `supercode run supercode`,
      exibimos o aquário em modo interativo.
    - Para ativar o LLM (orquestrador) a tarefa deve começar com o prefixo
      `super code` (com espaço). Ex: `super code adicione autenticação`.
      Ao detectar esse prefixo mostramos o aquário por 2s e então executamos.
    """
    task = (args.task or "").strip()

    # caso explícito: usuário só quer ver o aquário
    if task.lower() == "supercode":
        aquarium.main(task_label="supercode — pressione 'q' para sair", duration=None)
        return

    # exige prefixo de habilitação do LLM
    if not task.lower().startswith("super code"):
        print("Para ativar o LLM escreva a tarefa começando com 'super code'.\nEx: super code adicione autenticação nesse projeto")
        print("Ou execute `supercode` sem argumentos para ver o aquário interativo.")
        return

    # tarefa real (tira o prefixo)
    real_task = task[len("super code"):].strip()
    if not real_task:
        print("Tarefa vazia — depois do prefixo 'super code' descreva o que deseja.")
        return

    # mostramos o aquário como 'splash' por 2 segundos antes de ativar os agentes
    try:
        aquarium.main(task_label=f"Ativando LLM — {real_task}", duration=2.0)
    except Exception:
        # se o terminal não suportar curses, continuamos sem o splash
        pass

    providers = build_providers(args)
    orch = SuperCodeOrchestrator(
        project_root=args.project or ".",
        providers=providers,
        auto_yes=args.yes,
        on_event=event_printer,
    )

    print(f"{BOLD}SuperCode{RESET} — analisando o projeto em {Path(args.project or '.').resolve()}\n")
    result = orch.run_task(real_task)
    plan = result["plan"]

    print(f"\n{BOLD}{YELLOW}=== PLANO PROPOSTO ==={RESET}\n{plan}\n")

    if not args.yes:
        resp = input(f"{BOLD}Aplicar este plano? [y/N] {RESET}").strip().lower()
        if resp != "y":
            print("Cancelado. Nenhuma mudança foi feita.")
            return

    final = orch.confirm_and_implement(real_task, plan)

    print(f"\n{BOLD}{GREEN}=== RESUMO FINAL ==={RESET}")
    print(final["implementer_summary"])
    print(f"\n{BOLD}Revisão:{RESET}\n{final['review_summary']}")
    print(f"\n{BOLD}Testes:{RESET}\n{final['test_summary']}")
    print(f"\n{DIM}Diff completo disponível com: git -C {args.project or '.'} show HEAD{RESET}")


def cmd_init_config(args) -> None:
    from core.config import CONFIG_PATH

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists() and not args.force:
        print(f"Já existe um config em {CONFIG_PATH}. Use --force para sobrescrever.")
        return
    CONFIG_PATH.write_text(example_config_toml())
    print(f"Config de exemplo criado em {CONFIG_PATH}. Edite com suas API keys.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="supercode", description="Orquestrador multi-agente de programação.")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Executa uma tarefa no projeto atual")
    run_p.add_argument("task", help="Descrição da tarefa em linguagem natural")
    run_p.add_argument("--project", "-p", default=".", help="Diretório do projeto (default: .)")
    run_p.add_argument("--yes", "-y", action="store_true", help="Pula confirmações (aplica o plano automaticamente)")
    run_p.add_argument("--planner-provider", default="anthropic")
    run_p.add_argument("--planner-model", default=None)
    run_p.add_argument("--implementer-provider", default="openai")
    run_p.add_argument("--implementer-model", default=None)
    run_p.add_argument("--reviewer-provider", default="anthropic")
    run_p.add_argument("--reviewer-model", default=None)
    run_p.add_argument("--tester-provider", default="openai")
    run_p.add_argument("--tester-model", default=None)
    run_p.set_defaults(func=cmd_run)

    init_p = sub.add_parser("init-config", help="Cria um arquivo de config de exemplo")
    init_p.add_argument("--force", action="store_true")
    init_p.set_defaults(func=cmd_init_config)

    # subcomando direto para abrir o aquário
    aq_p = sub.add_parser("aquarium", help="Exibe o aquário interativo")
    aq_p.set_defaults(func=lambda args: aquarium.main(task_label="supercode — pressione 'q' para sair", duration=None))

    return parser


def main() -> None:
    parser = build_parser()

    # atalho: `supercode "tarefa"` sem precisar digitar `run`
    argv = sys.argv[1:]
    if argv and argv[0] not in ("run", "init-config", "aquarium", "-h", "--help"):
        argv = ["run"] + argv

    # atalho: nenhum argumento -> mostra o aquário interativo
    if not argv:
        aquarium.main(task_label="supercode — pressione 'q' para sair", duration=None)
        return

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
