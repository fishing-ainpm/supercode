"""
tools/file_tools.py

Ferramentas de leitura/escrita/edição de arquivos, restritas ao
diretório do projeto (evita path traversal pra fora do projeto).
"""

from __future__ import annotations

import os
from pathlib import Path

from providers.base import ToolSpec

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "target", "dist", "build", ".supercode"}


class FileTools:
    def __init__(self, project_root: str):
        self.root = Path(project_root).resolve()

    def _resolve(self, rel_path: str) -> Path:
        p = (self.root / rel_path).resolve()
        if self.root not in p.parents and p != self.root:
            raise PermissionError(f"Caminho fora do projeto: {rel_path}")
        return p

    def list_tree(self, max_depth: int = 4) -> str:
        lines = []
        root_depth = len(self.root.parts)
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
            depth = len(Path(dirpath).parts) - root_depth
            if depth > max_depth:
                dirnames[:] = []
                continue
            rel = Path(dirpath).relative_to(self.root)
            indent = "  " * depth
            if str(rel) != ".":
                lines.append(f"{indent}{rel.name}/")
            for f in sorted(filenames):
                lines.append(f"{indent}  {f}")
        return "\n".join(lines) if lines else "(projeto vazio)"

    def read_file(self, path: str) -> str:
        p = self._resolve(path)
        if not p.exists():
            return f"[erro] arquivo não existe: {path}"
        try:
            return p.read_text(errors="replace")
        except Exception as e:
            return f"[erro lendo {path}] {e}"

    def write_file(self, path: str, content: str) -> str:
        p = self._resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"escrito: {path} ({len(content)} bytes)"

    def edit_file(self, path: str, old_str: str, new_str: str) -> str:
        p = self._resolve(path)
        if not p.exists():
            return f"[erro] arquivo não existe: {path}"
        content = p.read_text()
        count = content.count(old_str)
        if count == 0:
            return f"[erro] old_str não encontrado em {path}"
        if count > 1:
            return f"[erro] old_str aparece {count} vezes em {path}; precisa ser único"
        p.write_text(content.replace(old_str, new_str, 1))
        return f"editado: {path}"

    # --- specs expostas aos agentes ---
    @staticmethod
    def specs() -> list[ToolSpec]:
        return [
            ToolSpec(
                name="list_tree",
                description="Lista a árvore de arquivos do projeto (respeitando .git, node_modules, etc).",
                parameters={"type": "object", "properties": {}, "required": []},
            ),
            ToolSpec(
                name="read_file",
                description="Lê o conteúdo de um arquivo do projeto.",
                parameters={
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "Caminho relativo ao root do projeto"}},
                    "required": ["path"],
                },
            ),
            ToolSpec(
                name="write_file",
                description="Cria ou sobrescreve um arquivo inteiro com o conteúdo dado.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
            ),
            ToolSpec(
                name="edit_file",
                description="Substitui uma ocorrência única de old_str por new_str num arquivo existente.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "old_str": {"type": "string"},
                        "new_str": {"type": "string"},
                    },
                    "required": ["path", "old_str", "new_str"],
                },
            ),
        ]
