# Specification

**Status:** FINALIZED
**Created:** 2026-04-21

## Synopsis

Implement the `AIServiceProtocol` and its concrete implementation `OllamaAIService` to provide news summarization, search query extraction, and factual response synthesis. This service acts as the "eyes and ears" of the Personal News Agent, processing raw information into concise, objective summaries and answers.

## Current Problem

The AI service layer is currently only defined in documentation (`ARCHITECTURE.md`) and does not exist in the codebase. There is no mechanism to communicate with the local Ollama instance to process news content.

## Ultimate Goal

Provide a reliable AI service that can summarize news, extract search queries, and synthesize responses based on facts, without injecting subjective analysis or creative ideas.

## Target Feature

Implementation of `AIServiceProtocol` using Ollama with the `gemma4:E4B` model.

## Requirements

### Must Have

- [ ] **Ubiquitous** The `AIServiceProtocol` shall be defined as a Python `Protocol` in `src/ai/protocol.py`.
- [ ] **Ubiquitous** The `OllamaAIService` shall implement `AIServiceProtocol` using the `gemma4:E4B` model.
- [ ] **When** summarizing news, the system shall produce a maximum of 2 concise sentences.
- [ ] **When** synthesizing a response, the system shall provide only factual information from the provided articles ("eyes and ears only"), avoiding any subjective analysis or original ideas.
- [ ] **Ubiquitous** All service methods shall be asynchronous.
- [ ] **If** the Ollama API is unavailable, the system shall raise a clear, catchable exception.

### Nice to Have

- [ ] **Where** configured, the model name and Ollama URL shall be loaded from environment variables.
- [ ] **Ubiquitous** The service shall include basic logging for prompt inputs and AI outputs.

### Won't Have

- Support for non-local AI backends (e.g., OpenAI, Anthropic) in this phase.
- Complex prompt chaining or multi-agent orchestration.

## Constraints

- Must use `gemma4:E4B` as the default model.
- Must adhere to the `NewsDTO` structure defined in `ARCHITECTURE.md`.
- Must run on Linux.

## Invariants & Must Preserve

- Strict typing for all protocol methods.
- Fact-only synthesis (no "brain" or creative analysis).

## Non-Goals / Rejected Approaches

- Providing AI-driven opinions or recommendations.
- Using cloud-based LLMs.

## Done Criteria

- `src/ai/protocol.py` and `src/ai/ollama_service.py` are created.
- The implementation successfully connects to a local Ollama instance.
- Summarization and synthesis follow the "eyes and ears only" constraint.
- Unit tests or a verification script confirm the functionality.

## Open Questions

- None.
