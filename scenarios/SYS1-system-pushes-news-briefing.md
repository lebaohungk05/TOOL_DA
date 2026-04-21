# Scenario: SYS1 - System Pushes News Briefing

## 1. Actor
- **Hệ thống (System):** Thành phần Scheduler và News Agent.
- **LLM Local:** Ollama (xử lý tóm tắt).

## 2. Trigger
- Đến các khung giờ cấu hình sẵn (Ví dụ: 08:00, 15:00, 22:00).

## 3. Pre-conditions
- Người dùng đã thực hiện lệnh `/start` và bot đã lưu lại `chat_id`.
- Người dùng đã thiết lập danh mục quan tâm hoặc sử dụng mặc định.
- Ollama đang chạy tại `localhost:11434`.
- Hệ thống có quyền truy cập Internet.

## 4. Main Flow
1. **Fetch & Filter:** Hệ thống quét tin mới từ các nguồn (RSS, NewsAPI), lọc theo chủ đề người dùng.
2. **Selection:** Chọn ra top 5 tin có độ ưu tiên cao nhất hoặc tin mới nhất.
3. **Summarization (Ollama):** Gửi dữ liệu raw của 5 tin sang Ollama. Ollama tóm tắt mỗi tin trong tối đa 2 câu súc tích.
4. **Formatting:** Đóng gói nội dung thành một tin nhắn Telegram có định dạng chuyên nghiệp:
    - Tiêu đề: "📅 BẢN TIN ĐỊNH KỲ - [Giờ] - [Ngày]"
    - Danh sách 5 tin kèm Emoji.
5. **Action Attachment:** Đính kèm Inline Buttons dưới tin nhắn:
    - `[🔍 Hỏi thêm về tin số 1]`
    - `[🔍 Hỏi thêm về tin số 2]`
    - ...
    - `[⚙️ Cài đặt]`
6. **Delivery:** Gửi tin nhắn đến người dùng.

## 5. Post-conditions
- Người dùng nhận được bản tin.
- Hệ thống lưu `news_metadata` (URL, tiêu đề) của 5 tin này vào Cache Session để phục vụ yêu cầu hỏi sâu.

## 6. Exception Scenarios
- **E1: Ollama không phản hồi:** Hệ thống gửi tin nhắn kèm tiêu đề và link gốc, ghi chú "Xin lỗi, module tóm tắt đang bận".
- **E2: Không có tin mới:** Gửi bản tin chung (General News) hoặc tin từ hôm qua kèm thông báo.

