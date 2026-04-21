phase: 4
created: 2026-04-21
is_tdd: false

---

# Plan: Phase 4 - Configuration & Observability

## Objective

Make the AI service configurable without code changes and provide visibility into LLM interactions for debugging and monitoring.

## V&V Strategy (Verification & Validation)

- **Verification:** 
    - Create a temporary `.env` file and verify the service uses its values via a print/test.
    - Configure the root logger to `DEBUG` in a test script and confirm LLM packets appear in stdout.
- **Validation:** Check that sensitive information is not logged at higher levels (INFO/WARNING).

## Spec Requirements (Traceability)

- [ ] Nice To Have: Load configuration from environment variables. (SPEC:35)
- [ ] Nice To Have: Basic logging for prompt inputs and AI outputs. (SPEC:36)

## Context

- ./.gtd/ai-service-implementation/SPEC.md
- ./.gtd/ai-service-implementation/ROADMAP.md
- ./.gtd/ai-service-implementation/4/RESEARCH.md
- src/ai/ollama_service.py

## Architecture Constraints

- **Single Source:** `.env` file and `os.environ`.
- **Invariants:** Default values must remain `http://localhost:11434` and `gemma4:E4B` if `.env` is missing.
- **Decision Rationale:** Using `python-dotenv` for local development following standard Python ecosystem patterns.

## Tasks

<task id="1" type="auto" complexity="Medium">
  <name>Implement Environment Configuration</name>
  <risk>Relative path issues when loading .env from different entry points.</risk>
  <files>src/ai/ollama_service.py</files>
  <requirement>
    **When** the service is initialized, **it shall** load `OLLAMA_HOST` and `OLLAMA_MODEL` from environment variables, falling back to defaults if not found.
  </requirement>
  <action>
    1. Install dependency: `uv pip install python-dotenv`.
    2. Import `os` and `dotenv` in `src/ai/ollama_service.py`.
    3. Update `OllamaAIService.__init__` to prioritize environment variables over hardcoded defaults.
    4. Call `load_dotenv()` at the module level or inside `__init__`.
  </action>
  <done>- Service initializes with values from `.env` (verified by passing a fake model in `.env` and seeing it in the service instance).</done>
</task>

<task id="2" type="auto" complexity="Medium">
  <name>Implement Diagnostic Logging</name>
  <risk>Noisy logs if not correctly leveled.</risk>
  <files>src/ai/ollama_service.py, scripts/test_observability.py</files>
  <requirement>
    **When** an LLM call is made, the system **shall** log the prompt and response at the `DEBUG` level.
  </requirement>
  <action>
    1. Initialize `logging.getLogger(__name__)` in `src/ai/ollama_service.py`.
    2. Add `logger.debug` calls in the `_call` method to capture the `messages` list and the raw `response` string.
    3. Create `scripts/test_observability.py` that configures logging and calls the service.
  </action>
  <done>- Running `scripts/test_observability.py` prints the prompt and AI response to the console when `DEBUG` is active.</done>
</task>

## Success Criteria

- [ ] Model name and URL are configurable via `.env`.
- [ ] Logs show outgoing prompts and incoming AI responses in `DEBUG` mode.
