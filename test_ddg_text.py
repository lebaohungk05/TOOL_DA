import asyncio
from ddgs import DDGS
from dotenv import load_dotenv

async def test_ddg_text():
    load_dotenv()
    query = "giá xăng dầu ngày 3/5/2026"
    print(f"Testing regular DDG search for: {query}")
    
    def search():
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=3))
            
    try:
        results = await asyncio.to_thread(search)
        print(f"Found {len(results)} results.")
        for r in results:
            print(f"- {r.get('title')} ({r.get('href')})")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ddg_text())
