# PRODUCT REQUIREMENTS DOCUMENT: PERSONAL NEWS AGENT BOT

## 1. TỔNG QUAN HỆ THỐNG
Hệ thống là một bot Telegram cá nhân hóa chạy trên môi trường Python local, tích hợp với Ollama để xử lý ngôn ngữ tự nhiên và DuckDuckGo để tìm kiếm thông tin thời gian thực. Hệ thống được thiết kế để hỗ trợ đa nền tảng (Windows/Linux) và ưu tiên xử lý dữ liệu tại chỗ.

## 2. KIẾN TRÚC KỸ THUẬT (TECHNICAL ARCHITECTURE)
- **Ngôn ngữ:** Python 3.10+ (Đảm bảo tính tương thích đa nền tảng).
- **Telegram Framework:** `aiogram 3.x` (Xử lý bất đồng bộ mạnh mẽ).
- **AI Backend:** Ollama API (Chạy tại localhost:11434).
    - **Models:** `gemma:4` hoặc `qwen:3.5` (Yêu cầu cấu hình trong hệ thống).
- **Database:** `SQLite` (Lưu trữ cục bộ tại `data/news_agent.db`).
- **Search Engine:** `duckduckgo-search` (Truy vấn tin tức thời gian thực).
- **Scheduler:** `APScheduler` (Quản lý đẩy tin định kỳ).

## 3. CHI TIẾT CHỨC NĂNG (FUNCTIONAL REQUIREMENTS)

### F1: Bản tin đẩy định kỳ (Scheduled Push Briefing)
- **Mục tiêu:** Tự động gửi tin tức tóm tắt theo lịch trình và sở thích.
- **Quy trình:**
    1. Quét tin từ RSS/News sources.
    2. Lọc tin dựa trên danh sách `block` (Exclusions).
    3. Ưu tiên tin dựa trên danh sách `follow` (Inclusions).
    4. Ollama thực hiện tóm tắt (Summarization) thành các đoạn ngắn.
- **Giao diện:** Tin nhắn Telegram với các nút Inline `🔍 Hỏi thêm về tin số X`.

### F2: Hội thoại sâu có ngữ cảnh (Contextual Deep-dive)
- **Mục tiêu:** Trả lời chi tiết về một tin tức cụ thể.
- **Qơ chế Focus Mode:**
    1. Khi nhấn nút "Hỏi thêm", Bot ghi nhớ ngữ cảnh tin tức đang chọn.
    2. Người dùng đặt câu hỏi cụ thể.
    3. Hệ thống tìm kiếm Web bổ trợ dựa trên: `[Tiêu đề tin] + [Câu hỏi người dùng]`.
    4. Ollama tổng hợp kết quả (Prompt Injection) để trả lời chi tiết.

### F3: Truy vấn tin tức tự do (Ad-hoc Search)
- **Mục tiêu:** Tìm kiếm mọi thông tin theo yêu cầu tức thời.
- **Quy trình:** Nhận input -> Ollama trích xuất Search Query -> Thực hiện tìm kiếm -> Ollama tổng hợp kết quả -> Trả lời kèm nguồn.

### F4: Quản lý sở thích cá nhân (Preference Management)
- **Lệnh `/follow [từ khóa]`:** Thêm từ khóa muốn ưu tiên.
- **Lệnh `/block [từ khóa]`:** Loại bỏ hoàn toàn các tin chứa từ khóa này.
- **Lệnh `/list`:** Hiển thị danh sách đang theo dõi/chặn và cho phép xóa nhanh bằng nút bấm.

## 4. CƠ SỞ DỮ LIỆU (DATABASE SCHEMA)
- **Users:** `user_id` (Primary Key), `chat_id`, `preferences_json`, `last_briefing`.
- **NewsCache:** `id`, `title`, `url`, `summary`, `timestamp` (Dùng để truy xuất nhanh khi deep-dive).

## 5. QUY TẮC TRIỂN KHAI (IMPLEMENTATION RULES)
- **Cross-platform:** Sử dụng thư viện `os` và `pathlib` để xử lý đường dẫn tương thích cả Win/Linux.
- **Error Handling:** Phải có cơ chế retry khi Ollama hoặc Internet gặp sự cố.
- **Privacy:** Dữ liệu hội thoại lưu local, chỉ gửi lệnh search đến DuckDuckGo.

## 6. CẤU TRÚC THƯ MỤC DỰ KIẾN
```text
news_agent/
├── src/
│   ├── bot/         # Logic xử lý Telegram
│   ├── ai/          # Giao tiếp với Ollama
│   ├── news/        # Crawler & Searcher
│   └── database/    # SQLite Manager
├── data/            # Lưu Database file
├── main.py          # Khởi chạy ứng dụng
└── requirements.txt # Thư viện cần thiết
```
