# Research: Phase 2 - Core Ollama Integration

## Objective
Integrate the `ollama` Python library to communicate with the local Ollama instance, ensuring strict typing and asynchronous operations.

## Findings

### Ollama Python Library
- **Library:** `ollama`
- **Installation:** `uv pip install ollama`
- **Async Usage:** Use `ollama.AsyncClient` for non-blocking calls.
- **Error Handling:** Use `ollama.ResponseError` for API-level errors and standard connection errors for network issues.

### Integration Pattern
```python
from ollama import AsyncClient, ResponseError

class OllamaAIService(AIServiceProtocol):
    def __init__(self, model: str = "gemma4:E4B", host: str = "http://localhost:11434"):
        self.client = AsyncClient(host=host)
        self.model = model

    async def _call_ollama(self, messages: list[dict]):
        try:
            response = await self.client.chat(model=self.model, messages=messages)
            return response.message.content
        except ResponseError as e:
            # Handle API errors
            raise AIServiceError(f"Ollama API error: {e.error}") from e
        except Exception as e:
            # Handle connection errors
            raise AIServiceConnectionError(f"Failed to connect to Ollama: {str(e)}") from e
```

### Invariants to Preserve
- **Strict Typing:** Must match `AIServiceProtocol`.
- **Async Everywhere:** All calls must be `async`.
- **Default Model:** `gemma4:E4B`.

## Recommendations
1. Install `ollama` dependency using `uv`.
2. Wrap `ollama.ResponseError` into project-specific exceptions to decouple the service from the library's internal error types at the interface level.
3. Use `AsyncClient` for all interactions to align with the `AIServiceProtocol`.
