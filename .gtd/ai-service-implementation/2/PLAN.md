phase: 2
created: 2026-04-21
is_tdd: false

---

# Plan: Phase 2 - Core Ollama Integration

## Objective

Establish a resilient connection between the Python application and the local Ollama service using the official `ollama` library. This phase focuses on the plumbing and error handling required for downstream AI tasks.

## V&V Strategy (Verification & Validation)

- **Verification:** Create `scripts/test_ollama_connection.py` to instantiate `OllamaAIService` and execute a basic ping/chat.
- **Validation:** Stop the local Ollama service and verify that `AIServiceConnectionError` is raised with a clear message.

## Spec Requirements (Traceability)

- [ ] Must Have: Implement `OllamaAIService` with `gemma4:E4B`. (SPEC:27)
- [ ] Must Have: Handle Ollama unavailability with clear exceptions. (SPEC:31)
- [ ] Must Have: All service methods shall be asynchronous. (SPEC:30)

## Context

- ./.gtd/ai-service-implementation/SPEC.md
- ./.gtd/ai-service-implementation/ROADMAP.md
- src/ai/protocol.py
- src/ai/ollama_service.py (to be created)

## Architecture Constraints

- **Single Source:** Ollama local API (localhost:11434).
- **Invariants:** Every method must remain `async`. Strict typing for return values.
- **Decision Rationale:** Using the official `ollama` library's `AsyncClient` for better maintained integration and easier error handling compared to manual HTTP calls.
- **Testability:** The service should allow injecting a custom `host` and `model` to facilitate testing with different environments.

## Tasks

<task id="1" type="auto" complexity="Medium">
  <name>Service Foundation & Dependency Injection</name>
  <risk>Missing dependency or mismatched protocol implementation.</risk>
  <files>src/ai/ollama_service.py</files>
  <requirement>
    **When** the service is initialized, **then** it shall configure the `AsyncClient` and define the custom exception hierarchy.
  </requirement>
  <action>
    1. Install dependency: `uv pip install ollama`.
    2. Create `src/ai/ollama_service.py`.
    3. Define `AIServiceError` (base) and `AIServiceConnectionError`.
    4. Implement `OllamaAIService` class implementing `AIServiceProtocol`.
    5. Initialize `ollama.AsyncClient` in `__init__`.
  </action>
  <done>- `src/ai/ollama_service.py` exists and implements `AIServiceProtocol`.
- `uv pip list` shows `ollama` installed.</done>
</task>

<task id="2" type="auto" complexity="High">
  <name>Connection Logic & Error Handling</name>
  <risk>Unhandled library-specific exceptions leaking into the orchestrator.</risk>
  <files>src/ai/ollama_service.py, scripts/test_ollama_connection.py</files>
  <requirement>
    **When** the system attempts to communicate with Ollama, **then** it shall catch connection/timeout/API errors and wrap them in `AIServiceConnectionError`.
  </requirement>
  <action>
    1. Implement a private `_call` method in `OllamaAIService` that wraps `await self.client.chat(...)`.
    2. Add `try/except` blocks for `ollama.ResponseError` and general connection errors (e.g., `httpx.ConnectError`).
    3. Implement `summarize_news` placeholder that uses `_call` to verify connectivity.
    4. Create `scripts/test_ollama_connection.py` representing a minimal usage example.
  </action>
  <done>- `scripts/test_ollama_connection.py` runs successfully when Ollama is up.
- Exception raised is `AIServiceConnectionError` when Ollama is down.</done>
</task>

## Success Criteria

- [ ] `OllamaAIService` successfully returns a response from a local `gemma4:E4B` model.
- [ ] Network failures result in a project-specific exception.
- [ ] Code is fully typed and passes `pyright`/`mypy`.
