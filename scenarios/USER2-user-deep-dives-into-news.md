# Scenario: USER2 - User Deep-dives into Specific News

## 1. Actor
- **Người dùng (User)**
- **Hệ thống (Bot + Ollama + Web Search Tool)**

## 2. Trigger
- Người dùng nhấn nút **"🔍 Hỏi thêm về tin số [X]"** từ bản tin.

## 3. Pre-conditions
- Bản tin đã được gửi.
- Metadata của tin số [X] khả dụng trong Session.
- Ollama đang hoạt động.

## 4. Main Flow
1. **Activation:** Người dùng nhấn nút. Bot xác nhận: *"OK, mình đang tập trung vào tin: [Tiêu đề tin X]. Bạn muốn biết chi tiết gì?"*.
2. **Context Locking:** Hệ thống chuyển trạng thái chat sang **Focus Mode** cho tin X.
3. **User Inquiry:** Người dùng gửi câu hỏi cụ thể (Ví dụ: "Chi tiết hợp đồng này là gì?").
4. **Context Enrichment:** 
    - Hệ thống dùng `duckduckgo-search` để tìm kiếm thông tin bổ sung dựa trên: `[Tiêu đề tin X] + [Câu hỏi người dùng]`.
    - Thu thập các snippet kết quả từ web search.
5. **LLM Processing (Ollama):** 
    - Build prompt gồm: Original News Info + Web Search Snippets + User Question.
    - Ollama phân tích và đưa ra câu trả lời dựa trên sự thật (Fact-based).
6. **Delivery:** Bot gửi câu trả lời kèm danh sách nguồn (Source links) đã tham khảo.
7. **Interactive Loop:** Người dùng tiếp tục đặt câu hỏi khác về tin X.
8. **Exit:** Người dùng nhấn nút **"🔚 Kết thúc chủ đề này"** hoặc hỏi về một tin khác.

## 5. Post-conditions
- Người dùng giải tỏa được thắc mắc chi tiết.
- Hệ thống giải phóng trạng thái Focus Mode khi kết thúc.

## 6. Exception Scenarios
- **E1: Không tìm thấy thông tin bổ sung:** Ollama trả lời dựa trên thông tin cũ hoặc thông báo không tìm thấy chi tiết yêu cầu.
- **E2: Câu hỏi không liên quan:** Bot gợi ý người dùng đặt câu hỏi đúng chủ đề hoặc thoát Focus Mode.
