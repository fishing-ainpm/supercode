"""
providers/anthropic_provider.py

Implementação do provedor Anthropic (Claude). Usa a API oficial de
Messages com tool use nativo.
"""

from __future__ import annotations

from typing import Optional

import requests

from .base import LLMProvider, LLMResponse, Message, ToolCall, ToolSpec

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def _headers(self) -> dict:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": API_VERSION,
            "content-type": "application/json",
        }

    def _to_anthropic_messages(self, messages: list[Message]) -> list[dict]:
        out = []
        for m in messages:
            if m.role == "tool":
                out.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": m.tool_call_id,
                        "content": m.content,
                    }],
                })
            elif m.role == "assistant" and m.tool_calls:
                blocks = []
                if m.content:
                    blocks.append({"type": "text", "text": m.content})
                for tc in m.tool_calls:
                    blocks.append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": tc.arguments,
                    })
                out.append({"role": "assistant", "content": blocks})
            else:
                out.append({"role": m.role, "content": m.content})
        return out

    def _to_anthropic_tools(self, tools: Optional[list[ToolSpec]]) -> list[dict]:
        if not tools:
            return []
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.parameters,
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
            "system": system_prompt,
            "messages": self._to_anthropic_messages(messages),
        }
        anth_tools = self._to_anthropic_tools(tools)
        if anth_tools:
            payload["tools"] = anth_tools

        resp = requests.post(API_URL, headers=self._headers(), json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        text = ""
        tool_calls = []
        for block in data.get("content", []):
            if block["type"] == "text":
                text += block["text"]
            elif block["type"] == "tool_use":
                tool_calls.append(ToolCall(id=block["id"], name=block["name"], arguments=block["input"]))

        return LLMResponse(
            text=text,
            tool_calls=tool_calls,
            stop_reason=data.get("stop_reason", ""),
            raw=data,
        )
