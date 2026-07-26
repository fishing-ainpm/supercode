"""
providers/__init__.py

Registro central de provedores. Adicionar um modelo novo = adicionar
uma entrada aqui (ver docs/ADDING_MODELS.md).
"""

from .base import LLMProvider, LLMResponse, Message, ToolCall, ToolSpec
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider

# name -> (classe, kwargs default)
REGISTRY: dict[str, type[LLMProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    # DeepSeek e qualquer outro OpenAI-compatible reusam OpenAIProvider
    # trocando só o base_url (ver docs/ADDING_MODELS.md).
    "deepseek": OpenAIProvider,
}


def build_provider(provider_name: str, api_key: str, model: str, **kwargs) -> LLMProvider:
    if provider_name not in REGISTRY:
        raise ValueError(
            f"Provedor desconhecido: '{provider_name}'. "
            f"Disponíveis: {', '.join(REGISTRY)}"
        )
    cls = REGISTRY[provider_name]
    return cls(api_key=api_key, model=model, **kwargs)
