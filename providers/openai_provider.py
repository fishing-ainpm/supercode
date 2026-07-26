"""
providers/openai_provider.py

Implementação do provedor OpenAI (GPT / Codex). Usa a Chat Completions
API com function calling. Também serve de base pra qualquer provedor
"OpenAI-compatible" (ex: DeepSeek, que a Lil já usa no claw-code) —
basta trocar `base_url`.
"""

from __future__ import annotations

import json
from typing import Optional

import requests

from .base import LLMProvider, LLMResponse, Message, ToolCall, ToolSpec


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _to_openai_messages(self, system_prompt: str, messages: list[Message]) -> list[dict]:
        out = [{"role": "system", "content": system_prompt}]
        for m in messages:
            if m.role == "tool":
                out.append({
                    "role": "tool",
                    "tool_call_id": m.tool_call_id,
                    "content": m.content,
                })
            elif m.role == "assistant" and m.tool_calls:
                out.append({
                    "role": "assistant",
                    "content": m.content or None,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                        }
                        for tc in m.tool_calls
                    ],
                })
            else:
                out.append({"role": m.role, "content": m.content})
        return out

    def _to_openai_tools(self, tools: Optional[list[ToolSpec]]) -> list[dict]:
        if not tools:
            return []
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in tools
        ]

    def chat(
        self,
        system_prompt: str,
        messages: list[Message],
        tools: Optional[list[ToolSpec]] = None,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": self._to_openai_messages(system_prompt, messages),
        }
        oa_tools = self._to_openai_tools(tools)
        if oa_tools:
            payload["tools"] = oa_tools

        resp = requests.post(f"{self.base_url}/chat/completions", headers=self._headers(), json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        msg = choice["message"]
        text = msg.get("content") or ""
        tool_calls = []
        for tc in msg.get("tool_calls") or []:
            tool_calls.append(ToolCall(
                id=tc["id"],
                name=tc["function"]["name"],
                arguments=json.loads(tc["function"]["arguments"] or "{}"),
            ))

        return LLMResponse(
            text=text,
            tool_calls=tool_calls,
            stop_reason=choice.get("finish_reason", ""),
            raw=data,
        )
