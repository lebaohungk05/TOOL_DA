# 📑 DỰ ÁN: GLOBAL SENTIMENT INTELLIGENCE AGENT (GSIA) - LOCAL EDITION
**Hệ thống phân tích đa nguồn, đa ngôn ngữ chạy 100% Cục bộ & Miễn phí**

---

## 🎯 1. MỤC TIÊU CHIẾN LƯỢC (ZERO COST)
1.  **Chi phí:** 0 VNĐ (Sử dụng hoàn toàn mô hình mã nguồn mở).
2.  **Quyền riêng tư:** 100% dữ liệu xử lý Local, không gửi ra ngoài qua API.
3.  **Quy mô:** Xử lý 10.000 - 100.000+ bài báo (VnExpress, Reuters, Bloomberg...).
4.  **Phần cứng:** Tối ưu hóa cho GPU NVIDIA T2000 (4GB VRAM) bằng kỹ thuật CPU+GPU Hybrid.

---

## 🛠 2. KẾ HOẠCH THỰC HIỆN (8 TUẦN)

### THÁNG THỨ NHẤT: XÂY DỰNG PIPELINE TỰ CUNG TỰ CẤP

#### Tuần 1: High-Scale Data Acquisition (Crawl dữ liệu)
*   **Công việc:** Sử dụng Scrapy (Asynchronous) để crawl đa nguồn.
*   **Database:** Cài đặt PostgreSQL Local.
*   **Kết quả:** Thu thập 10.000 bài báo đầu tiên.

#### Tuần 2: Local Multilingual Preprocessing
*   **Công việc:** 
    *   Sử dụng `langdetect` nhận diện ngôn ngữ.
    *   Dùng `Helsinki-NLP/opus-mt` (Local) nếu cần dịch thuật cơ bản.
    *   Deduplication bằng thuật toán MinHash để tiết kiệm RAM.

#### Tuần 3: Local Sentiment Analysis (Small Models)
*   **Công việc:** 
    *   Triển khai **DistilPhoBERT** (cho tiếng Việt) và **DistilBERT** (cho tiếng Anh).
    *   Các model này chỉ nặng ~200MB, chạy cực nhanh trên T2000.
*   **Kết quả:** Phân loại cảm xúc tự động cho hàng chục nghìn bài báo.

#### Tuần 4: Intelligence Layer (Ollama & Phi-3 Mini)
*   **Công việc:** 
    *   Cài đặt **Ollama** và chạy mô hình **Phi-3 Mini (3.8B)**.
    *   Viết script Python để nạp các cụm tin tức vào Phi-3 để lấy tóm tắt và định hướng (Zero Cost).
*   **Kết quả:** AI đưa ra nhận định chiến lược mà không cần Internet.

---

### THÁNG THỨ HAI: AUTOMATION & ACADEMIC FINALIZATION

#### Tuần 5: Automation & Scheduling
*   **Công việc:** Sử dụng `Task Scheduler` (Windows) hoặc `Cron` để tự động hóa việc crawl và phân tích mỗi đêm.

#### Tuần 6: Local Visualization Dashboard
*   **Công việc:** Sử dụng **Streamlit** để tạo giao diện hiển thị biểu đồ và kết quả phân tích trực tiếp từ PostgreSQL.

#### Tuần 7: Validation (Đánh giá học thuật)
*   **Công việc:** So sánh độ chính xác của Local LLM (Phi-3) với dữ liệu thực tế. Viết báo cáo LaTeX.

#### Tuần 8: Demo & Final Presentation
*   **Công việc:** Trình diễn khả năng chạy Offline hoàn toàn của hệ thống - một điểm cộng cực lớn về mặt kỹ thuật và bảo mật.

---

## 💻 3. CHIẾN LƯỢC TỐI ƯU CHO T2000 (4GB VRAM)
1.  **Ollama Management:** Chỉ khởi động mô hình LLM khi cần xử lý tóm tắt, sau đó tắt để giải phóng VRAM cho các tác vụ khác.
2.  **Quantization (Q4_K_M):** Sử dụng các bản nén 4-bit của mô hình để đảm bảo chạy mượt trong 4GB VRAM.
3.  **Batching:** Xử lý theo từng lô (batch) 100 bài báo một lần để kiểm soát RAM.

---

## 📊 4. TECH STACK (100% FREE)
*   **LLM:** Ollama (Phi-3 Mini 3.8B / Llama 3 8B Q4).
*   **NLP:** HuggingFace Transformers, SpaCy, Underthesea.
*   **Storage:** PostgreSQL.
*   **UI:** Streamlit.
*   **Language:** Python 3.10.
