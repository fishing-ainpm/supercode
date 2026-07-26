"""
agents/base.py

Todo agente é: um system prompt especializado + um provedor de LLM +
um conjunto de tools que ele tem permissão de usar. O loop de
tool-use (chamar o modelo, executar tools, devolver resultado, repetir
até o modelo parar de pedir tools) é genérico e vive aqui.
"""

from __future__ import annotations

from typing import Callable, Optional

from providers.base import LLMProvider, Message, ToolCall, ToolSpec


class Agent:
    name: str = "agent"
    system_prompt: str = ""

    def __init__(
        self,
        provider: LLMProvider,
        tools: Optional[list[ToolSpec]] = None,
        tool_executor: Optional[Callable[[ToolCall], str]] = None,
        max_turns: int = 20,
    ):
        self.provider = provider
        self.tools = tools or []
        self.tool_executor = tool_executor
        self.max_turns = max_turns
        self.history: list[Message] = []

    def run(self, user_input: str, on_tool_call=None, on_text=None) -> str:
        """
        Roda o loop até o modelo terminar (stop_reason != tool_use)
        ou até bater max_turns. Retorna o texto final do agente.
        """
        self.history.append(Message(role="user", content=user_input))
        final_text = ""

        for _ in range(self.max_turns):
            response = self.provider.chat(
                system_prompt=self.system_prompt,
                messages=self.history,
                tools=self.tools or None,
            )

            if response.text and on_text:
                on_text(self.name, response.text)
            final_text = response.text or final_text

            if not response.tool_calls:
                self.history.append(Message(role="assistant", content=response.text))
                break

            self.history.append(Message(
                role="assistant", content=response.text, tool_calls=response.tool_calls
            ))

            for tc in response.tool_calls:
                if on_tool_call:
                    on_tool_call(self.name, tc)
                result = self.tool_executor(tc) if self.tool_executor else "[sem executor de tools configurado]"
                self.history.append(Message(role="tool", content=str(result), tool_call_id=tc.id))

        return final_text
