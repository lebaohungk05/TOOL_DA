# Roadmap

**Spec:** ./.gtd/ai-service-implementation/SPEC.md
**Current Problem:** The AI service layer is currently only defined in documentation and does not exist in the codebase.
**Ultimate Goal:** Provide a reliable AI service that can summarize news, extract search queries, and synthesize responses based on facts, without injecting subjective analysis.
**Target Feature:** Implementation of `AIServiceProtocol` using Ollama with the `gemma4:E4B` model.
**Created:** 2026-04-21

## Strategy

The roadmap follows a foundation-first approach, starting with the definition of interfaces and data structures, followed by the core implementation of the Ollama service, and finally refining the prompt logic to ensure factual accuracy.

## Constraints & Invariants

- Constraint: Must use `gemma4:E4B` as the default model.
- Constraint: Must adhere to the `NewsDTO` structure.
- Must Preserve: Strict typing for all protocol methods.
- Must Preserve: Fact-only synthesis ("eyes and ears only").

## Must-Haves

- [ ] Define `AIServiceProtocol` in `src/ai/protocol.py`.
- [ ] Implement `OllamaAIService` with `gemma4:E4B`.
- [ ] Summarization: max 2 concise sentences.
- [ ] Synthesis: factual information only.
- [ ] All service methods shall be asynchronous.
- [ ] Handle Ollama unavailability with clear exceptions.

## Nice-To-Haves

- [ ] Load configuration from environment variables.
- [ ] Basic logging for prompts and outputs.

## Phases

### Phase 1: Foundation & Interface

**Status**: ✅ Complete
**Objective**: **When** this phase is complete, the system shall have a clearly defined `AIServiceProtocol` and the necessary data structures (`NewsDTO`) to support AI operations.

**Covers Requirements:**
- [x] Must Have: Define `AIServiceProtocol` in `src/ai/protocol.py`.
- [x] Must Have: Adhere to the `NewsDTO` structure.
- [x] Must Have: All service methods shall be asynchronous.

**Exit Criteria:**
- [x] `src/ai/protocol.py` exists with `AIServiceProtocol` defined.
- [x] `src/models.py` (or equivalent) exists with `NewsDTO` and `UserConfigDTO` defined.
- [x] Code passes type checking (mypy/pyright).

### Phase 2: Core Ollama Integration

**Status**: ✅ Complete
**Objective**: **When** this phase is complete, the `OllamaAIService` shall be able to communicate with a local Ollama instance and handle connection errors.

**Covers Requirements:**
- [x] Implement `OllamaAIService` with `gemma4:E4B`.
- [x] Handle Ollama unavailability with clear exceptions.

Exit criteria:
- [x] `src/ai/ollama_service.py` implements `AIServiceProtocol`.
- [x] Service can successfully ping/call the Ollama API.
- [x] Exception is raised when Ollama is unreachable.

### Phase 3: Factual Processing Logic

**Status**: ✅ Complete
**Objective**: **When** this phase is complete, the AI service shall provide objective summaries and factual responses as per the "eyes and ears" constraint.

**Covers Requirements:**
- [x] Summarization: max 2 concise sentences.
- [x] Synthesis: factual information only.
- [x] Extract search keywords from user prompts.

**Exit Criteria:**
- [x] `summarize_news` produces <= 2 sentences.
- [x] `synthesize_response` excludes subjective analysis.
- [x] `extract_search_queries` returns relevant keywords.

### Phase 4: Configuration & Observability (Optional)

**Status**: ✅ Complete
**Objective**: **When** this phase is complete, the service shall be configurable via environment variables and provide visibility into its operations.

**Covers Requirements:**
- [x] Nice to Have: Load configuration from environment variables.
- [x] Nice to Have: Basic logging for prompts and outputs.

**Exit Criteria:**
- [x] Model name and URL are configurable via `.env`.
- [x] Logs show outgoing prompts and incoming AI responses.
