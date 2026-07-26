"""
core/orchestrator.py

O SuperCode em si: liga project + tools + agentes + memory num
pipeline único: planner -> (confirmação humana) -> implementer ->
reviewer -> tester -> resumo + registro em memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from agents.specialized import ImplementerAgent, PlannerAgent, ReviewerAgent, TesterAgent
from memory.session import Session
from providers.base import LLMProvider, ToolCall
from tools.file_tools import FileTools
from tools.git_tools import GitTools
from tools.shell_tools import ShellTools


@dataclass
class Providers:
    planner: LLMProvider
    implementer: LLMProvider
    reviewer: LLMProvider
    tester: LLMProvider


class SuperCodeOrchestrator:
    def __init__(
        self,
        project_root: str,
        providers: Providers,
        confirm_fn: Optional[Callable[[str], bool]] = None,
        auto_yes: bool = False,
        on_event: Optional[Callable[[str, str], None]] = None,
    ):
        self.project_root = project_root
        self.providers = providers
        self.on_event = on_event or (lambda kind, text: None)

        self.file_tools = FileTools(project_root)
        self.git_tools = GitTools(project_root)
        self.shell_tools = ShellTools(project_root, confirm_fn=confirm_fn, auto_yes=auto_yes)
        self.session = Session(project_root)

        self.git_tools.ensure_repo()

    # --- executor genérico de tools, roteia pelo nome ---
    def _make_executor(self, allow_write: bool, allow_shell: bool) -> Callable[[ToolCall], str]:
        def executor(tc: ToolCall) -> str:
            try:
                if tc.name == "list_tree":
                    return self.file_tools.list_tree()
                if tc.name == "read_file":
                    return self.file_tools.read_file(tc.arguments["path"])
                if tc.name == "write_file":
                    if not allow_write:
                        return "[negado] este agente não tem permissão de escrita"
                    return self.file_tools.write_file(tc.arguments["path"], tc.arguments["content"])
                if tc.name == "edit_file":
                    if not allow_write:
                        return "[negado] este agente não tem permissão de escrita"
                    return self.file_tools.edit_file(tc.arguments["path"], tc.arguments["old_str"], tc.arguments["new_str"])
                if tc.name == "run_command":
                    if not allow_shell:
                        return "[negado] este agente não tem permissão de executar comandos"
                    return self.shell_tools.run_command(tc.arguments["command"])
                return f"[erro] tool desconhecida: {tc.name}"
            except Exception as e:
                return f"[erro executando {tc.name}] {e}"
        return executor

    def run_task(self, task: str) -> dict:
        """Executa o pipeline completo pra uma tarefa. Retorna um dict com plan/summary/etc."""
        file_specs = self.file_tools.specs()
        shell_specs = self.shell_tools.specs()

        # 1. PLANEJAMENTO (somente leitura)
        self.on_event("stage", "planejamento")
        planner = PlannerAgent(
            provider=self.providers.planner,
            tools=file_specs,
            tool_executor=self._make_executor(allow_write=False, allow_shell=False),
        )
        context = self.session.recent_context()
        plan = planner.run(
            f"Contexto de tarefas anteriores neste projeto:\n{context}\n\nTarefa atual: {task}",
            on_text=lambda name, text: self.on_event("agent_text", f"[{name}] {text}"),
            on_tool_call=lambda name, tc: self.on_event("tool_call", f"[{name}] {tc.name}({tc.arguments})"),
        )

        return {"stage": "plan_ready", "plan": plan, "task": task}

    def confirm_and_implement(self, task: str, plan: str) -> dict:
        """Chamado depois que o usuário aprova o plano."""
        file_specs = self.file_tools.specs()
        shell_specs = self.shell_tools.specs()

        self.git_tools.checkpoint(f"antes de: {task}")

        # 2. IMPLEMENTAÇÃO (leitura + escrita + shell)
        self.on_event("stage", "implementação")
        implementer = ImplementerAgent(
            provider=self.providers.implementer,
            tools=file_specs + shell_specs,
            tool_executor=self._make_executor(allow_write=True, allow_shell=True),
        )
        impl_summary = implementer.run(
            f"Plano aprovado:\n{plan}\n\nExecute-o agora no projeto.",
            on_text=lambda name, text: self.on_event("agent_text", f"[{name}] {text}"),
            on_tool_call=lambda name, tc: self.on_event("tool_call", f"[{name}] {tc.name}({tc.arguments})"),
        )

        # 3. REVISÃO (leitura + escrita, sem shell)
        self.on_event("stage", "revisão")
        reviewer = ReviewerAgent(
            provider=self.providers.reviewer,
            tools=file_specs,
            tool_executor=self._make_executor(allow_write=True, allow_shell=False),
        )
        review_summary = reviewer.run(
            f"Mudanças feitas pelo implementador:\n{impl_summary}\n\nRevise o código alterado.",
            on_text=lambda name, text: self.on_event("agent_text", f"[{name}] {text}"),
            on_tool_call=lambda name, tc: self.on_event("tool_call", f"[{name}] {tc.name}({tc.arguments})"),
        )

        # 4. TESTES (leitura + shell, sem escrita livre de código — só cria testes)
        self.on_event("stage", "testes")
        tester = TesterAgent(
            provider=self.providers.tester,
            tools=file_specs + shell_specs,
            tool_executor=self._make_executor(allow_write=True, allow_shell=True),
        )
        test_summary = tester.run(
            f"Contexto da tarefa: {task}\nMudanças: {impl_summary}\n\nValide a solução.",
            on_text=lambda name, text: self.on_event("agent_text", f"[{name}] {text}"),
            on_tool_call=lambda name, tc: self.on_event("tool_call", f"[{name}] {tc.name}({tc.arguments})"),
        )

        diff = self.git_tools.diff()
        self.git_tools.commit_changes(f"supercode: {task}")

        final_summary = (
            f"## Implementação\n{impl_summary}\n\n"
            f"## Revisão\n{review_summary}\n\n"
            f"## Testes\n{test_summary}"
        )
        self.session.record_task(task, plan, final_summary)

        return {
            "stage": "done",
            "implementer_summary": impl_summary,
            "review_summary": review_summary,
            "test_summary": test_summary,
            "diff": diff,
        }
