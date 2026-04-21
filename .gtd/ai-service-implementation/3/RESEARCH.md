# Research: Phase 3 - Factual Processing Logic

## Objective
Design and verify prompt strategies for summarization, keyword extraction, and factual synthesis using the `gemma4:E4B` model.

## Findings

### Prompt Strategies

#### 1. Summarization
- **Constraint:** Max 2 sentences.
- **Prompt:** 
  ```text
  You are an objective news summarizer.
  Summarize the following content in exactly 1 or 2 concise, factual sentences.
  Do not add any analysis or opinion.
  
  Content: {raw_content}
  ```

#### 2. Keyword Extraction
- **Prompt:**
  ```text
  You are a search query designer.
  Extract 3 to 5 key search terms from the following user request that would help find relevant news articles.
  Return only a comma-separated list of keywords.
  
  User Request: {user_prompt}
  ```
- **Post-processing:** Split by comma and strip whitespace.

#### 3. Factual Synthesis
- **Constraint:** "Eyes and ears only", no subjective analysis.
- **Prompt:**
  ```text
  You are a factual assistant. 
  Answer the question based ONLY on the provided articles.
  If the information is not in the articles, say "I don't have enough information."
  Do not add your own opinions or creative ideas.
  
  Question: {question}
  
  Articles:
  {formatted_articles}
  ```

### Invariants to Preserve
- **Truthfulness:** The system must not hallucinate beyond the provided text in synthesis.
- **Conciseness:** Summaries must strictly stay within 2 sentences.

### Testing Seams
- We can create a `scripts/verify_prompts.py` that uses the `OllamaAIService` to run these specific scenarios and manually inspect the quality/length.
