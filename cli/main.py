#!/usr/bin/env python3
"""
cli/main.py

Ponto de entrada: `supercode "adicione autenticação nesse projeto"`
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import example_config_toml, resolve_provider_config
from core.orchestrator import Providers, SuperCodeOrchestrator
from providers import build_provider

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
    providers = build_providers(args)
    orch = SuperCodeOrchestrator(
        project_root=args.project or ".",
        providers=providers,
        auto_yes=args.yes,
        on_event=event_printer,
    )

    print(f"{BOLD}SuperCode{RESET} — analisando o projeto em {Path(args.project or '.').resolve()}\n")
    result = orch.run_task(args.task)
    plan = result["plan"]

    print(f"\n{BOLD}{YELLOW}=== PLANO PROPOSTO ==={RESET}\n{plan}\n")

    if not args.yes:
        resp = input(f"{BOLD}Aplicar este plano? [y/N] {RESET}").strip().lower()
        if resp != "y":
            print("Cancelado. Nenhuma mudança foi feita.")
            return

    final = orch.confirm_and_implement(args.task, plan)

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

    return parser


def main() -> None:
    parser = build_parser()

    # atalho: `supercode "tarefa"` sem precisar digitar `run`
    argv = sys.argv[1:]
    if argv and argv[0] not in ("run", "init-config", "-h", "--help"):
        argv = ["run"] + argv

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
