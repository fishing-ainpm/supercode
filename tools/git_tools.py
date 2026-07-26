"""
tools/git_tools.py

Wrappers finos sobre git, usados pelo orquestrador (não expostos
diretamente como tool de LLM por padrão) pra: snapshot antes de
mudanças grandes, diff de revisão, e commit no final.
"""

from __future__ import annotations

import subprocess


class GitTools:
    def __init__(self, project_root: str):
        self.root = project_root

    def _run(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True
        )
        return (result.stdout + result.stderr).strip()

    def is_repo(self) -> bool:
        return self._run("rev-parse", "--is-inside-work-tree") == "true"

    def ensure_repo(self) -> None:
        if not self.is_repo():
            self._run("init")

    def status(self) -> str:
        return self._run("status", "--short")

    def diff(self) -> str:
        return self._run("diff")

    def checkpoint(self, message: str) -> str:
        """Cria um commit de checkpoint antes de uma mudança grande, pra permitir rollback."""
        self._run("add", "-A")
        return self._run("commit", "-m", f"[supercode-checkpoint] {message}", "--allow-empty")

    def commit_changes(self, message: str) -> str:
        self._run("add", "-A")
        return self._run("commit", "-m", message)

    def rollback_to_checkpoint(self) -> str:
        return self._run("reset", "--hard", "HEAD")
