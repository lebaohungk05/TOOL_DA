# Entrypoints

**Generated:** 2026-04-21
**Last Updated:** 2026-04-21
**Last Verified:** 2026-04-21

| Entrypoint | Type | File | Purpose | Evidence |
| ---------- | ---- | ---- | ------- | -------- |
| Verify Prompts | Script | `scripts/verify_prompts.py` | Validates all AI service logic | scripts/verify_prompts.py:5 |
| Test Ollama | Script | `scripts/test_ollama_connection.py` | Verifies low-level Ollama connectivity | scripts/test_ollama_connection.py:5 |

## Startup Flows

### AI Service Diagnostic Flow

1. User runs `scripts/test_ollama_connection.py`.
2. Script instantiates `OllamaAIService`.
3. Service loads configuration from `.env` via `load_dotenv(override=True)`.
4. Service pings local Ollama API via `AsyncClient.chat`.

Evidence: scripts/test_ollama_connection.py:6, src/ai/ollama_service.py:34
