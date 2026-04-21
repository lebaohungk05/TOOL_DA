# Research: Phase 4 - Configuration & Observability

## Objective
Enable environment-based configuration and diagnostic logging for the AI service.

## Findings

### Configuration
- **Library:** `python-dotenv` is standard for loading `.env` files.
- **Variables:**
    - `OLLAMA_HOST`: The URL for the Ollama server (default: `http://localhost:11434`).
    - `OLLAMA_MODEL`: The model name (default: `gemma4:E4B`).
- **Implementation:** Load during service initialization or via a config DTO.

### Observability
- **Library:** Standard `logging` module.
- **Points of Interest:**
    - Log outgoing prompts (at `DEBUG` level).
    - Log incoming responses (at `DEBUG` level).
    - Log errors (already handled via exceptions, but could be logged at the boundary).
- **Security:** Ensure prompts don't leak PII if logging is enabled in production (not a concern for this local-only bot yet).

### Pattern for Config
```python
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
model = os.getenv("OLLAMA_MODEL", "gemma4:E4B")
```

## Recommendations
1. Install `python-dotenv`.
2. Add a `LOGGER = logging.getLogger(__name__)` to `ollama_service.py`.
3. Wrap logger calls in `_call` to see all LLM traffic.
