import asyncio
from src.ai import OllamaAIService
from src.models import NewsDTO

async def run_comprehensive_test():
    service = OllamaAIService()
    
    # 1. Summarization Test
    print("--- 1. Testing Summarization (Target: <= 2 sentences) ---")
    content = (
        "The global semiconductor industry is facing new challenges as demand for AI chips surges. "
        "Taiwan Semiconductor Manufacturing Co (TSMC) reported a significant increase in revenue for the first quarter, "
        "driven by high demand from clients like NVIDIA and Apple. However, supply chain constraints remain a concern "
        "as manufacturers struggle to keep up with the rapid pace of AI development. Analysts predict a strong year ahead "
        "but warn of potential geopolitical risks affecting production."
    )
    summary = await service.summarize_news(content)
    print(f"Summary: {summary}")
    sentence_count = summary.count(".")
    print(f"Sentence count estimate: {sentence_count}")
    
    # 2. Keyword Extraction Test
    print("\n--- 2. Testing Keyword Extraction ---")
    prompt = "Get news about solar energy investments in Southeast Asia for 2026."
    keywords = await service.extract_search_queries(prompt)
    print(f"Keywords: {keywords}")
    
    # 3. Factual Synthesis Test
    print("\n--- 3. Testing Factual Synthesis ---")
    articles = [
        NewsDTO(
            article_id="A1",
            title="UN Climate Report",
            source="Reuters",
            url="url",
            raw_content="Global temperatures rose by 1.1 degrees Celsius compared to pre-industrial levels. "
                        "The report emphasizes that urgent action is needed by 2030."
        )
    ]
    q = "By what year is urgent action needed according to the report?"
    res = await service.synthesize_response(articles, q)
    print(f"Question: {q}\nSynthesized Answer: {res}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
