"""
memory/session.py

Estado persistido por projeto em <projeto>/.supercode/session.json:
histórico de tarefas executadas, plano da última rodada, etc. Isso
é o que permite o SuperCode "lembrar" o que já foi feito num projeto
entre execuções, sem precisar reler tudo do zero.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


class Session:
    def __init__(self, project_root: str):
        self.dir = Path(project_root) / ".supercode"
        self.path = self.dir / "session.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                pass
        return {"tasks": []}

    def save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))

    def record_task(self, task: str, plan: str, summary: str) -> None:
        self.data.setdefault("tasks", []).append({
            "timestamp": time.time(),
            "task": task,
            "plan": plan,
            "summary": summary,
        })
        self.save()

    def recent_context(self, n: int = 3) -> str:
        tasks = self.data.get("tasks", [])[-n:]
        if not tasks:
            return "(nenhuma tarefa anterior registrada)"
        lines = []
        for t in tasks:
            lines.append(f"- Tarefa: {t['task']}\n  Resumo: {t['summary']}")
        return "\n".join(lines)
