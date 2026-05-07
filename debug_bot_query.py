import asyncio
import logging
import os
from dotenv import load_dotenv

from src.ai import AIService
from src.ai.providers import get_provider
from src.news.rss_crawler import RSSCrawler
from src.news.fetchers.smart_fetcher import SmartFetcher

async def debug_bot_query():
    load_dotenv()
    
    print("\n--- DEBUGGING BOT AD-HOC QUERY FLOW ---")
    
    provider = get_provider()
    ai_service = AIService(provider=provider)
    fetcher = SmartFetcher()
    news_repo = RSSCrawler(fetcher=fetcher)
    
    user_input = "giá xăng dầu ngày 3/5/2026"
    lang = "vi"
    
    print(f"User Input: {user_input}")
    
    # 1. AI Extract Search Query
    try:
        search_term = await ai_service.extract_search_queries(user_input, lang)
        print(f"AI Search Term: '{search_term}'")
    except Exception as e:
        print(f"AI Extraction Failed: {e}")
        search_term = user_input

    # 2. Final Query Logic (from briefing_service.py)
    final_query = search_term if search_term and len(search_term) > 2 else user_input
    print(f"Final Query used for search: '{final_query}'")
    
    # 3. Web Search
    print(f"Initiating Web Search for: '{final_query}'")
    try:
        results = await news_repo.search_web(final_query, limit=3)
        print(f"Web Search Results: {len(results)} found.")
    except Exception as e:
        print(f"Web Search Failed: {e}")
        
    # 4. Test with FULL natural language query (simulating AI failure)
    print(f"\n--- TESTING WITH FULL NATURAL LANGUAGE QUERY ---")
    print(f"Query: '{user_input}'")
    try:
        results = await news_repo.search_web(user_input, limit=3)
        print(f"Web Search Results: {len(results)} found.")
    except Exception as e:
        print(f"Web Search Failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_bot_query())
