import asyncio
import sys
import os
from playwright.async_api import async_playwright

async def debug_screenshot():
    query = "giá xăng dầu"
    url = f"https://search.brave.com/news?q={query}"
    print(f"--- CAPTURING BRAVE SCREENSHOT ---")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(5)
        await page.screenshot(path="brave_debug.png")
        print(f"Saved: brave_debug.png")
        
        # In mã HTML để soi
        content = await page.content()
        print(f"Length: {len(content)}")
        print(f"Snippet: {content[:1000]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_screenshot())
