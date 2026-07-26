"""
providers/base.py

Interface unificada que todo provedor de LLM precisa implementar.
Isso é o que permite o SuperCode usar Claude, GPT/Codex, ou qualquer
outro modelo futuro sem mudar uma linha de código nos agentes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ToolSpec:
    """Descrição de uma tool no formato interno do SuperCode."""
    name: str
    description: str
    parameters: dict  # JSON Schema (formato "properties"/"required")


@dataclass
class ToolCall:
    """Uma chamada de tool que o modelo decidiu fazer."""
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    """Resposta normalizada de qualquer provedor."""
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = ""  # "end_turn" | "tool_use" | "max_tokens" | etc
    raw: Any = None


@dataclass
class Message:
    role: str  # "user" | "assistant" | "tool"
    content: str = ""
    tool_call_id: Optional[str] = None   # quando role == "tool"
    tool_calls: list[ToolCall] = field(default_factory=list)  # quando role == "assistant" pediu tools


class LLMProvider(ABC):
    """Todo provedor (Anthropic, OpenAI, futuro...) implementa isso."""

    name: str = "base"

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.extra = kwargs

    @abstractmethod
    def chat(
        self,
        system_prompt: str,
        messages: list[Message],
        tools: Optional[list[ToolSpec]] = None,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Envia a conversa e retorna a resposta normalizada."""
        raise NotImplementedError

    def supports_tools(self) -> bool:
        return True
