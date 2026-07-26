"""
core/config.py

Carrega configuração de (em ordem de prioridade):
1. Flags de linha de comando
2. Variáveis de ambiente
3. Arquivo ~/.config/supercode/config.toml
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "supercode" / "config.toml"

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-5-codex",
    "deepseek": "deepseek-v4-pro",
}

DEFAULT_BASE_URLS = {
    "deepseek": "https://api.deepseek.com/v1",
}


@dataclass
class ProviderConfig:
    provider: str
    api_key: str
    model: str
    base_url: str | None = None


def _load_toml() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "rb") as f:
            return tomllib.load(f)
    return {}


def resolve_provider_config(provider_name: str, model_override: str | None = None) -> ProviderConfig:
    toml_data = _load_toml()
    section = toml_data.get(provider_name, {})

    env_key_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
    }
    env_var = env_key_map.get(provider_name, f"{provider_name.upper()}_API_KEY")
    api_key = os.environ.get(env_var) or section.get("api_key")

    if not api_key:
        raise RuntimeError(
            f"Nenhuma API key encontrada para '{provider_name}'. "
            f"Defina {env_var} ou configure em {CONFIG_PATH}."
        )

    model = model_override or section.get("model") or DEFAULT_MODELS.get(provider_name)
    base_url = section.get("base_url") or DEFAULT_BASE_URLS.get(provider_name)

    return ProviderConfig(provider=provider_name, api_key=api_key, model=model, base_url=base_url)


def example_config_toml() -> str:
    return '''# ~/.config/supercode/config.toml
#
# Só precisa preencher os provedores que você vai usar. As chaves
# também podem vir de variáveis de ambiente (ANTHROPIC_API_KEY,
# OPENAI_API_KEY, DEEPSEEK_API_KEY) — env var tem prioridade sobre
# este arquivo.

[anthropic]
api_key = "sk-ant-..."
model = "claude-sonnet-4-6"

[openai]
api_key = "sk-..."
model = "gpt-5-codex"

[deepseek]
api_key = "sk-..."
model = "deepseek-v4-pro"
base_url = "https://api.deepseek.com/v1"

[defaults]
planner = "anthropic"
implementer = "openai"
reviewer = "anthropic"
tester = "openai"
'''
