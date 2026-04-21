import asyncio
import logging
import sys
from src.ai import OllamaAIService

async def test_logging():
    # Configure logging to stdout
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s:%(name)s:%(message)s",
        stream=sys.stdout
    )
    
    service = OllamaAIService()
    print("Executing service call with DEBUG logging active...")
    try:
        await service.summarize_news("Factual processing verification.")
    except Exception as e:
        print(f"Service call failed (as expected if model/env not set), checking logs above: {e}")

if __name__ == "__main__":
    asyncio.run(test_logging())
