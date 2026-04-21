import asyncio
from src.ai import OllamaAIService

async def verify_task_1():
    service = OllamaAIService()
    prompt = "Tell me about the latest developments in NVIDIA's AI chips and their competitors like AMD."
    print(f"Prompt: {prompt}")
    keywords = await service.extract_search_queries(prompt)
    print(f"Extracted Keywords: {keywords}")
    if isinstance(keywords, list) and len(keywords) > 0:
        print("Verification Task 1 SUCCESS")
    else:
        print("Verification Task 1 FAILED")

if __name__ == "__main__":
    asyncio.run(verify_task_1())
