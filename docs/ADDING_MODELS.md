# Adicionando novos modelos / provedores

O SuperCode isola toda a diferença entre LLMs atrás da interface
`LLMProvider` (`providers/base.py`). Adicionar um modelo novo é, na
prática, um dos dois casos abaixo.

## Caso 1: o provedor é "OpenAI-compatible" (a maioria dos casos)

Muitos provedores (DeepSeek, Groq, Together, um servidor local via
Ollama/vLLM com endpoint compatível, etc) implementam a mesma API de
Chat Completions da OpenAI. Nesse caso **não precisa escrever código
nenhum** — só registrar em `providers/__init__.py`:

```python
REGISTRY = {
    ...,
    "meu_provedor": OpenAIProvider,
}
```

E no `config.toml`:

```toml
[meu_provedor]
api_key = "..."
model = "nome-do-modelo"
base_url = "https://api.meuprovedor.com/v1"
```

É exatamente assim que o DeepSeek já está configurado.

## Caso 2: o provedor tem uma API própria (ex: Anthropic, Gemini, etc)

1. Crie `providers/meu_provedor.py` implementando `LLMProvider`:

```python
from .base import LLMProvider, LLMResponse, Message, ToolCall, ToolSpec

class MeuProvedorProvider(LLMProvider):
    name = "meu_provedor"

    def chat(self, system_prompt, messages, tools=None, max_tokens=4096):
        # 1. converta `messages` (lista de Message) pro formato da API
        # 2. converta `tools` (lista de ToolSpec) pro formato de function
        #    calling da API
        # 3. faça a chamada HTTP
        # 4. normalize a resposta em LLMResponse (text + tool_calls)
        ...
        return LLMResponse(text=..., tool_calls=[...], stop_reason=...)
```

2. Registre em `providers/__init__.py`:

```python
from .meu_provedor import MeuProvedorProvider
REGISTRY["meu_provedor"] = MeuProvedorProvider
```

3. Adicione o modelo default em `core/config.py` (`DEFAULT_MODELS`) se
   fizer sentido.

Pronto — os 4 agentes já podem usar `--planner-provider meu_provedor`
sem nenhuma outra mudança, porque `agents/` e `core/orchestrator.py`
só conhecem a interface `LLMProvider`, nunca uma API específica.

## Testando um provedor novo sem gastar tokens de verdade

Use um provedor "fake" pra validar o pipeline (loop de tool-use,
permissões, git checkpoint) sem chamar nenhuma API real — é assim que
o MVP foi validado durante o desenvolvimento:

```python
class FakeProvider(LLMProvider):
    def __init__(self, script):
        super().__init__("fake-key", "fake-model")
        self.script = list(script)  # lista de LLMResponse pré-definidas

    def chat(self, system_prompt, messages, tools=None, max_tokens=4096):
        return self.script.pop(0)
```
