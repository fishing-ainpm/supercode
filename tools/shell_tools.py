"""
tools/shell_tools.py

Execução de comandos no terminal. TODO comando passa por confirmação
do usuário antes de rodar — não existe modo "silencioso" pra shell,
de propósito (é a superfície mais perigosa do agente).
"""

from __future__ import annotations

import subprocess
from typing import Callable, Optional

from providers.base import ToolSpec

ConfirmFn = Callable[[str], bool]


class ShellTools:
    def __init__(self, project_root: str, confirm_fn: Optional[ConfirmFn] = None, auto_yes: bool = False):
        self.root = project_root
        self.auto_yes = auto_yes
        self.confirm_fn = confirm_fn or (lambda cmd: input(f"Rodar `{cmd}`? [y/N] ").strip().lower() == "y")

    def run_command(self, command: str, timeout: int = 120) -> str:
        if not self.auto_yes and not self.confirm_fn(command):
            return "[cancelado pelo usuário]"
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            out = result.stdout[-4000:]
            err = result.stderr[-2000:]
            return f"exit_code={result.returncode}\nstdout:\n{out}\nstderr:\n{err}"
        except subprocess.TimeoutExpired:
            return f"[erro] comando excedeu {timeout}s"
        except Exception as e:
            return f"[erro] {e}"

    @staticmethod
    def specs() -> list[ToolSpec]:
        return [
            ToolSpec(
                name="run_command",
                description=(
                    "Executa um comando shell no diretório do projeto. "
                    "Requer confirmação do usuário antes de executar. "
                    "Use para rodar testes, linters, builds, gerenciadores de pacote, etc."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Comando shell completo a executar"},
                    },
                    "required": ["command"],
                },
            ),
        ]
