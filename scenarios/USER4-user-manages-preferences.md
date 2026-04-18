# Scenario: USER4 - Managing Interests & Blocks

## 1. Actor
- **Người dùng (User)**
- **Hệ thống (Bot + Database)**

## 2. Trigger
- Người dùng sử dụng các lệnh điều hướng sở thích: `/follow`, `/block`, `/list`.

## 3. Pre-conditions
- Bot đã hoạt động và Database đã sẵn sàng.

## 4. Main Flow

### A. Thêm chủ đề quan tâm
1. **Action:** Người dùng gõ lệnh `/follow [chủ đề]` (Ví dụ: `/follow Ngoại hạng Anh`).
2. **Processing:** 
    - Hệ thống lưu [chủ đề] vào danh sách `Inclusions`.
    - Nếu [chủ đề] này từng nằm trong danh sách `Exclusions`, hệ thống sẽ tự động gỡ bỏ khỏi danh sách đó.
3. **Notify:** Bot gửi tin nhắn xác nhận đã theo dõi thành công.

### B. Loại bỏ chủ đề không muốn xem
1. **Action:** Người dùng gõ lệnh `/block [chủ đề]` (Ví dụ: `/block Bóng chuyền`).
2. **Processing:** 
    - Hệ thống lưu [chủ đề] vào danh sách `Exclusions`.
    - Nếu [chủ đề] này từng nằm trong danh sách `Inclusions`, hệ thống sẽ tự động gỡ bỏ khỏi danh sách đó.
3. **Notify:** Bot gửi tin nhắn xác nhận đã chặn thành công.

### C. Xem danh sách cấu hình
1. **Action:** Người dùng gõ lệnh `/list`.
2. **Processing:** Hệ thống truy vấn DB và trả về danh sách các từ khóa `Inclusions` và `Exclusions` hiện tại.

## 5. Logic lọc tin (Filtering Logic)
1. **Hard Exclusion:** Hệ thống lọc bỏ tất cả tin tức có tiêu đề hoặc nội dung chứa từ khóa trong danh sách `Exclusions`.
2. **Priority Inclusion:** Các tin có chứa từ khóa trong danh sách `Inclusions` sẽ được ưu tiên cao nhất khi tóm tắt bản tin hàng ngày.

## 6. Post-conditions
- Trải nghiệm tin tức được cá nhân hóa sâu theo từng từ khóa người dùng cung cấp.

## 7. Exception Scenarios
- **E1: Lệnh thiếu nội dung:** Nếu người dùng chỉ gõ `/follow` mà không có tên chủ đề, Bot sẽ hướng dẫn cách sử dụng đúng.
