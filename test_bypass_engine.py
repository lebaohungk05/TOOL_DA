from curl_cffi import requests
import asyncio

def test_bypass():
    # Thử lại đúng cái link Reuters vừa nãy đã chặn chúng ta
    url = "https://www.reuters.com/technology/ai-startups-race-develop-smarter-robots-2024-04-20/"
    
    print(f"--- ĐANG SỬ DỤNG BYPASS ENGINE (CURL_CFFI) ---")
    print(f"Bắt chước: Google Chrome 110")
    print(f"URL: {url}\n")

    try:
        # Lệnh impersonate này sẽ giả mạo TLS Fingerprint
        response = requests.get(url, impersonate="chrome110", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("[v] THÀNH CÔNG! Đã lọt qua hàng rào bảo vệ của Reuters.")
            print(f"Độ dài nội dung: {len(response.text)} ký tự")
            
            # Kiểm tra xem có lấy được nội dung bài báo thật không
            if "AI startups" in response.text or "<article" in response.text:
                print("[!] Xác nhận: Nội dung trả về là bài báo thật, không phải trang lỗi.")
                print(f"\nMột đoạn văn bản lấy được:\n{response.text[5000:6000]}...")
        else:
            print(f"[x] Vẫn bị chặn! Lỗi: {response.status_code}")
            
    except Exception as e:
        print(f"[!] Lỗi kỹ thuật: {str(e)}")

if __name__ == "__main__":
    test_bypass()
