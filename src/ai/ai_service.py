import logging
from typing import Optional

from src.ai.protocol import AIServiceProtocol
from src.ai.providers.protocol import LLMProviderProtocol
from src.models import NewsDTO
from src.core.i18n import get_text
from src.database.protocol import StorageProtocol

logger = logging.getLogger(__name__)


class AIService(AIServiceProtocol):
    """
    Core AI Service implementation bridging domain use cases to generic LLM providers.
    
    This service treats the AI as 'eyes and ears only', focusing on factual
    processing and summarization without subjective analysis. Relies on the
    injected provider (Ollama, OpenAI, etc.) for actual LLM communication.
    """

    def __init__(self, provider: LLMProviderProtocol, storage: Optional[StorageProtocol] = None):
        """
        Initialize the AI service with a specific LLM Provider and optional Storage.
        
        Args:
            provider: Adaptive port implementation for the selected LLM.
            storage: Optional persistence layer for user configs and caching.
        """
        self.provider = provider
        self.storage = storage

    async def summarize_news(self, raw_content: str, language: str = "vi") -> str:
        """
        Summarize news content into a maximum of 2 sentences in the target language.
        """
        prompt = get_text("prompt_summarizer", language, content=raw_content)
        messages = [{"role": "user", "content": prompt}]
        return await self.provider.chat(messages)

    async def extract_search_queries(self, user_prompt: str, language: str = "vi") -> str:
        """
        Produce a single search-optimized string.
        """
        prompt = get_text("prompt_query_designer", language, user_prompt=user_prompt)
        messages = [{"role": "user", "content": prompt}]
        response = await self.provider.chat(messages)
        
        return response.strip().strip('"')

    def _format_articles(self, articles: list[NewsDTO]) -> str:
        """Format articles into a text block for the LLM."""
        formatted = []
        for i, art in enumerate(articles, 1):
            formatted.append(
                f"--- Article {i} ---\n"
                f"Title: {art.title}\n"
                f"Source: {art.source}\n"
                f"Content: {art.raw_content or art.summary}\n"
            )
        return "\n".join(formatted)

    async def synthesize_response(self, articles: list[NewsDTO], question: str, language: str = "vi") -> str:
        """
        Synthesize a factual response based on provided articles and a question.
        """
        formatted_articles = self._format_articles(articles)
        prompt = get_text(
            "prompt_synthesizer", 
            language, 
            articles=formatted_articles, 
            question=question
        )
        messages = [{"role": "user", "content": prompt}]
        return await self.provider.chat(messages)

    async def select_related_feeds(self, keyword: str, categories_dict: dict[str, list[str]], language: str = "vi") -> dict[str, list[str]]:
        """
        Analyze a keyword and select which categories across publishers are highly related to it.
        """
        import json
        import hashlib
        
        # Sort keys and lists to ensure deterministic hash of current sources
        sorted_dict = {
            k: sorted(v) for k, v in sorted(categories_dict.items())
        }
        serialized = json.dumps(sorted_dict, sort_keys=True, ensure_ascii=False)
        current_hash = hashlib.md5(serialized.encode('utf-8')).hexdigest()
        
        # Check cache if storage is available
        if self.storage:
            try:
                cached = await self.storage.get_feed_selection_cache(keyword)
                if cached:
                    cached_hash = cached["categories_hash"]
                    if cached_hash == current_hash:
                        logger.info("Cache hit for feed selection on keyword '%s'. Reusing cached feeds.", keyword)
                        return cached["selected_feeds"]
                    else:
                        logger.info(
                            "Cache mismatch for feed selection on keyword '%s'. Current hash: %s, Cached hash: %s. Re-running LLM.",
                            keyword,
                            current_hash,
                            cached_hash,
                        )
            except Exception as e:
                logger.warning("Failed to read feed selection cache for keyword '%s': %s", keyword, e)
        
        # Serialize the category mapping dictionary for clean prompt embedding
        categories_json = json.dumps(categories_dict, ensure_ascii=False, indent=2)
        prompt = get_text(
            "prompt_feed_selector",
            language,
            keyword=keyword,
            categories_json=categories_json
        )
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.provider.chat(messages)
        
        logger.info(
            "LLM raw response for feed selection on keyword '%s':\n%s",
            keyword,
            response,
        )
        
        # Clean potential markdown block wrappers from the LLM response
        cleaned_response = response.strip()
        if cleaned_response.startswith("```"):
            lines = cleaned_response.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_response = "\n".join(lines).strip()
            
        try:
            selected = json.loads(cleaned_response)
            if not isinstance(selected, dict):
                logger.warning("LLM feed selector response is not a JSON object, falling back to empty selection.")
                return {}
            # Clean up the parsed dictionary to ensure strict type compliance
            cleaned_selected: dict[str, list[str]] = {}
            for k, v in selected.items():
                if isinstance(v, list):
                    cleaned_selected[k] = [str(item) for item in v]
            
            logger.info(
                "Parsed feed mappings for keyword '%s': %s",
                keyword,
                cleaned_selected,
            )
            
            # Save to cache if storage is available
            if self.storage and cleaned_selected:
                try:
                    await self.storage.save_feed_selection_cache(keyword, current_hash, cleaned_selected)
                    logger.info("Saved feed selection for keyword '%s' to cache.", keyword)
                except Exception as e:
                    logger.warning("Failed to save feed selection cache for keyword '%s': %s", keyword, e)
            
            return cleaned_selected
        except Exception as e:
            logger.warning("Failed to parse LLM feed selector JSON response: %s. Raw response: %s", e, response)
            return {}
