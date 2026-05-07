import asyncio
from playwright.async_api import async_playwright

async def test_bypass_cnn():
    # CNN là trang lớn, không bị chặn DNS ở VN, nhưng có rào cản bot
    url = "https://edition.cnn.com/world"
    
    print(f"--- TESTING BYPASS WITH CNN ---")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"[*] Accessing CNN: {url}")
        
        try:
            # Truy cập và đợi trang nạp xong
            response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print(f"[*] HTTP Status: {response.status}")
            
            if response.status == 200:
                print("[v] SUCCESS! CNN bypassed.")
                title = await page.title()
                print(f"Page Title: {title}")
                
                # In ra một số tiêu đề tin từ CNN
                headlines = await page.locator("span.container__headline-text").all_inner_texts()
                print("\nTop 5 CNN Headlines:")
                for h in headlines[:5]:
                    print(f"- {h}")
            else:
                print(f"[x] Failed. Status: {response.status}")
        except Exception as e:
            print(f"[!] Error: {str(e)}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_bypass_cnn())
