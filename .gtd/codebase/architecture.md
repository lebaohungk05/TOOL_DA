# Architecture

**Generated:** 2026-04-21
**Last Updated:** 2026-04-21
**Last Verified:** 2026-04-21

## Tech Stack

| Layer | Technology | Evidence |
| ----- | ---------- | -------- |
| Language | Python 3.13 | ARCHITECTURE.md:98, .venv/lib/python3.13 |
| Package Manager | uv | GEMINI.md:1 |
| LLM Backend | Ollama (Local) | src/ai/ollama_service.py:34 |
| HTTP Client | httpx | src/ai/ollama_service.py:2 (via ollama lib) |

## Project Structure

- `src/`: Core source code
    - `ai/`: AI orchestration and service implementations
    - `models.py`: Shared data transfer objects (DTOs)
- `scripts/`: Diagnostic and verification scripts
- `.gtd/`: Project management and design documentation

Evidence: ls -R src:1-10

## Major Subsystems

### AI Orchestration

- Type: Domain / Infrastructure
- Path: `src/ai/`
- Purpose: Provides an abstraction layer for LLM operations (summarize, synthesize, extract keywords).
- Depends on: `src.models`
- Used by: Not yet integrated (placeholder directories in `src/bot`, `src/news`)
- Evidence: src/ai/protocol.py:4, src/ai/ollama_service.py:15
