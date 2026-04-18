# Scenario: USER3 - User Searches for Any News

## 1. Actor
- **Người dùng (User)**
- **Hệ thống (Bot + Ollama + Web Search Tool)**

## 2. Trigger
- Người dùng gửi một câu hỏi trực tiếp hoặc một từ khóa cho Bot (Ví dụ: "Giá Bitcoin hôm nay", "Tin mới về OpenAI").

## 3. Pre-conditions
- Bot đang hoạt động bình thường.
- Ollama và Internet khả dụng.

## 4. Main Flow
1. **Input Analysis:** Hệ thống tiếp nhận yêu cầu từ người dùng qua tin nhắn văn bản.
2. **Search Query Generation (Ollama):** Hệ thống dùng Ollama để chuyển đổi câu hỏi tự nhiên thành các từ khóa tìm kiếm (Search terms) hiệu quả.
3. **Web Searching:** Thực hiện tìm kiếm qua `duckduckgo-search` để lấy thông tin mới nhất từ internet.
4. **Information Retrieval:** Thu thập các đoạn văn bản (snippets) và tiêu đề từ top 3-5 kết quả tìm kiếm.
5. **Synthesis (Ollama):** 
    - Đưa toàn bộ các đoạn snippet và câu hỏi gốc vào Ollama.
    - Ollama tổng hợp câu trả lời ngắn gọn, trung thực dựa trên các dữ liệu vừa tìm được.
6. **Delivery:** Bot gửi câu trả lời cho người dùng, đính kèm các liên kết nguồn minh bạch.
7. **Refinement:** Đính kèm các nút bấm gợi ý để người dùng có thể hỏi sâu hơn hoặc mở rộng sang chủ đề liên quan.

## 5. Post-conditions
- Người dùng có được thông tin mong muốn theo yêu cầu tức thời.

## 6. Exception Scenarios
- **E1: Truy vấn không rõ ràng:** Bot yêu cầu người dùng làm rõ ý định nếu câu hỏi quá ngắn hoặc mơ hồ.
- **E2: Không tìm thấy kết quả:** Bot thông báo không tìm thấy tin tức liên quan trong thời gian gần đây và gợi ý từ khóa khác.
