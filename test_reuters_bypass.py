import httpx
import asyncio

async def test_reuters_fetch():
    # Một link bài báo thực tế của Reuters
    url = "https://www.reuters.com/technology/ai-startups-race-develop-smarter-robots-2024-04-20/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    print(f"--- ĐANG THỬ FETCH REUTERS BẰNG HTTPX ---")
    print(f"URL: {url}\n")
    
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            response = await client.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("Lấy được dữ liệu, nhưng hãy xem nội dung có gì...")
                print(f"Độ dài nội dung: {len(response.text)}")
                print(f"1000 ký tự đầu tiên:\n{response.text[:1000]}")
            else:
                print(f"Thất bại! Reuters trả về lỗi: {response.status_code}")
                
    except Exception as e:
        print(f"Lỗi kết nối: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_reuters_fetch())
