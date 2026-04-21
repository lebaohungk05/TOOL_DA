phase: 3
created: 2026-04-21
is_tdd: false

---

# Plan: Phase 3 - Factual Processing Logic

## Objective

Implement the core AI processing logic for the news agent. This phase ensures the AI acts as an objective observer, providing concise summaries, optimized search queries, and strictly factual responses without subjective injection.

## V&V Strategy (Verification & Validation)

- **Verification:** Create `scripts/verify_prompts.py` to test each service method against predefined inputs and check against constraints (sentence count, data type).
- **Validation:** Manual inspection of synthesis output to ensure no "brain" (opinion/advice) is present.

## Spec Requirements (Traceability)

- [ ] Must Have: Summarization: max 2 concise sentences. (SPEC:28)
- [ ] Must Have: Synthesis: factual information only ("eyes and ears only"). (SPEC:29)
- [ ] Must Have: Extract search keywords from user prompts. (ROADMAP:73)

## Context

- ./.gtd/ai-service-implementation/SPEC.md
- ./.gtd/ai-service-implementation/ROADMAP.md
- ./.gtd/ai-service-implementation/3/RESEARCH.md
- src/ai/ollama_service.py

## Architecture Constraints

- **Single Source:** Provided `raw_content` or `articles` list.
- **Invariants:** 
    - No external knowledge used in synthesis beyond the provided articles.
    - Summaries strictly <= 2 sentences.
- **Decision Rationale:** Using system prompts to enforce constraints at the LLM level, supplemented by light post-processing (e.g., splitting CSV strings for keywords).

## Tasks

<task id="1" type="auto" complexity="Medium">
  <name>Implement Keyword Extraction & Post-processing</name>
  <risk>LLM might return conversational filler instead of a clean list of keywords.</risk>
  <files>src/ai/ollama_service.py</files>
  <requirement>
    **When** requested to extract search queries, the system shall return a list of 3-5 strings representing search terms.
  </requirement>
  <action>
    1. Update `extract_search_queries` in `src/ai/ollama_service.py`.
    2. Implement a system prompt that requests a comma-separated list.
    3. Implement post-processing to clean and split the LLM response into a `list[str]`.
  </action>
  <done>- `extract_search_queries("Tell me about Apple's new VR headset")` returns a list like `['Apple', 'VR headset', 'Vision Pro']` (or similar relevant terms).</done>
</task>

<task id="2" type="auto" complexity="Medium">
  <name>Implement Factual Synthesis & Article Formatting</name>
  <risk>LLM hallucinating or adding "As an AI, I think..." style commentary.</risk>
  <files>src/ai/ollama_service.py</files>
  <requirement>
    **When** synthesizing a response, the system shall use only provided articles and answer the question objectively.
  </requirement>
  <action>
    1. Implement a private `_format_articles` helper to convert `list[NewsDTO]` into a readable text block for the LLM.
    2. Update `synthesize_response` to combine formatted articles and the user's question into a "Factual Assistant" prompt.
    3. Ensure the prompt explicitly forbids opinions.
  </action>
  <done>- `synthesize_response` returns answers grounded in article text.
- Returns "I don't have enough information" if data is missing.</done>
</task>

<task id="3" type="auto" complexity="Low">
  <name>Refine Summarization & Verify All Prompts</name>
  <risk>Sentence count limit might be ignored by the model if the prompt is weak.</risk>
  <files>src/ai/ollama_service.py, scripts/verify_prompts.py</files>
  <requirement>
    **When** summarizing, the model shall consistently produce 1-2 sentences.
  </requirement>
  <action>
    1. Update `summarize_news` prompt with stronger instructions for the 2-sentence limit.
    2. Create `scripts/verify_prompts.py` covering all three methods with test data.
    3. Run the verification script and adjust prompts if necessary.
  </action>
  <done>- `summarize_news` output has no more than 2 periods/sentences.
- All Phase 3 methods verified with successful script output.</done>
</task>

## Success Criteria

- [ ] `summarize_news` consistently produces <= 2 sentences.
- [ ] `extract_search_queries` returns a list of cleaned strings.
- [ ] `synthesize_response` is factual and avoids subjective analysis.
