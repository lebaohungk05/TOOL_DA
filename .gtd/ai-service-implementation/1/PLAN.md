phase: 1
created: 2026-04-21
is_tdd: false

---

# Plan: Phase 1 - Foundation & Interface

## Objective

Define the core data structures (`NewsDTO`, `UserConfigDTO`) and the `AIServiceProtocol` to establish a clear contract for the AI service layer. This ensures all components use a consistent data format and allows for interchangeable AI backends.

## V&V Strategy (Verification & Validation)

- **Static Analysis:** Use `mypy` or `pyright` to verify that the `AIServiceProtocol` is correctly defined and that the DTOs are properly typed.
- **Manual Verification:** Inspect the created files to ensure they match the definitions in `ARCHITECTURE.md`.

## Spec Requirements (Traceability)

- [ ] Must Have: The `AIServiceProtocol` shall be defined as a Python `Protocol` in `src/ai/protocol.py`.
- [ ] Must Have: Adhere to the `NewsDTO` structure defined in `ARCHITECTURE.md`.
- [ ] Must Have: All service methods shall be asynchronous.

## Context

- ./.gtd/ai-service-implementation/SPEC.md
- ./.gtd/ai-service-implementation/ROADMAP.md
- ARCHITECTURE.md

## Architecture Constraints

- **Single Source:** `src/models.py` is the authoritative source for data transfer objects.
- **Invariants:** All protocol methods must be `async`.
- **Decision Rationale:** Using `Protocol` (Structural Subtyping) allows for flexible implementation without rigid inheritance.
- **Testability:** The protocol provides a clear seam for mocking the AI service in other modules.
- **Non-Goals:** This phase does not include any logic for calling Ollama or processing prompts.

## Tasks

<task id="1" type="auto" complexity="Low">
  <name>Define Data Transfer Objects (DTOs)</name>
  <risk>None. Standard boilerplate for data classes.</risk>
  <files>src/models.py</files>
  <requirement>
    **Ubiquitous** The system shall use `NewsDTO` and `UserConfigDTO` as defined in `ARCHITECTURE.md`.
  </requirement>
  <action>
    Create `src/models.py` and implement `NewsDTO` and `UserConfigDTO` using `dataclasses`.
  </action>
  <done>`src/models.py` exists with correctly typed `NewsDTO` and `UserConfigDTO` classes.</done>
</task>

<task id="2" type="auto" complexity="Low">
  <name>Define AIServiceProtocol</name>
  <risk>None. Simple interface definition.</risk>
  <files>src/ai/protocol.py</files>
  <requirement>
    **Ubiquitous** The `AIServiceProtocol` shall be defined as a Python `Protocol` in `src/ai/protocol.py`.
  </requirement>
  <action>
    Create `src/ai/protocol.py` and define `AIServiceProtocol` with `summarize_news`, `extract_search_queries`, and `synthesize_response` methods.
  </action>
  <done>`src/ai/protocol.py` exists with the `AIServiceProtocol` interface correctly defined and typed.</done>
</task>

## Success Criteria

- [ ] `src/models.py` and `src/ai/protocol.py` are created.
- [ ] All methods in `AIServiceProtocol` are marked as `async`.
- [ ] `NewsDTO` includes all fields required by the architecture (article_id, title, url, source, raw_content, summary, published_at).
