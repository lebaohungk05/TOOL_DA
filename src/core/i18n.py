from typing import Any

# Localization dictionary for UI strings and AI Prompts
I18N: dict[str, dict[str, str]] = {
    "vi": {
        # UI
        "briefing_header": "📅 *BẢN TIN ĐỊNH KỲ*",
        "details_button": "🔍 Chi tiết tin số {i}",
        "settings_button": "⚙️ Cài đặt",
        "source_label": "Nguồn",
        "sources_header": "📖 *CÁC NGUỒN THAM KHẢO:*",
        "source_link_text": "Nguồn {i}",
        "end_topic_button": "🔚 Kết thúc chủ đề này",
        "no_news_found": "Không tìm thấy tin mới cho bản tin của bạn.",
        "error_system": "⚠️ Có lỗi hệ thống xảy ra khi tạo bản tin.",
        "error_context_not_found": "Xin lỗi, không tìm thấy ngữ cảnh tin tức gốc.",
        "error_deep_dive": "⚠️ Có lỗi xảy ra khi xử lý yêu cầu tìm hiểu sâu của bạn.",
        "focus_mode_entered": "🔍 Bạn đang trong chế độ tập trung. Hãy đặt câu hỏi về tin này, hoặc bấm nút kết thúc.",
        "focus_mode_exited": "✅ Đã thoát chế độ tập trung.",
        "ad_hoc_searching": "🔍 Đang tìm kiếm thông tin cho yêu cầu của bạn...",
        "settings_not_implemented": "🚧 Tính năng cài đặt đang được phát triển.",
        "desc_start": "Bắt đầu onboarding",
        "desc_follow": "Theo dõi từ khóa",
        "desc_block": "Chặn từ khóa",
        "desc_unrelated": "Bật/tắt nhận tin không liên quan",
        "desc_list": "Xem cấu hình",
        "desc_brief": "Tạo bản tin ngay lập tức",
        "desc_unfollow": "Xóa từ khóa theo dõi",
        "desc_unblock": "Xóa từ khóa chặn",
        "desc_lang": "Thay đổi ngôn ngữ hiển thị",
        "lang_updated": "🌐 Ngôn ngữ đã được cập nhật thành Tiếng Việt.",
        
        # Onboarding
        "onboarding_choose_language": "🌐 Chọn ngôn ngữ / Choose your language:",
        "onboarding_welcome": "✅ Xin chào! Tôi là News Agent Bot.\n\n📰 Tôi sẽ tự động gửi bản tin tóm tắt cho bạn vào lúc {times}.\n🔍 Khi nhận bản tin, bạn có thể bấm nút để tìm hiểu sâu hơn.\n\nDùng /follow <từ khóa> để theo dõi chủ đề, /block <từ khóa> để chặn, /list để xem cấu hình.",
        
        # Commands
        "cmd_brief_triggering": "⏳ Đang tạo bản tin tức thời cho bạn...",
        "cmd_follow_added": "✅ Đã thêm từ khóa theo dõi: {keyword}",
        "cmd_block_added": "🚫 Đã thêm từ khóa chặn: {keyword}",
        "cmd_follow_removed": "✅ Đã xóa từ khóa theo dõi: {keyword}",
        "cmd_block_removed": "✅ Đã xóa từ khóa chặn: {keyword}",
        "cmd_keyword_not_found": "Không tìm thấy từ khóa: {keyword}",
        "cmd_missing_keyword": "Vui lòng nhập từ khóa. Ví dụ: /follow AI",
        "cmd_list_header": "⚙️ Cấu hình của bạn:\n\n📌 Theo dõi: {follow}\n🚫 Chặn: {block}\n⏰ Giờ nhận tin: {times}\n🌐 Ngôn ngữ: {language}\n📦 Nhận tin không liên quan: {unrelated}\n📡 Số nguồn tin tự chọn: {custom_feeds_count}",
        "cmd_user_not_found": "Bạn chưa đăng ký. Hãy gửi /start để bắt đầu.",
        "cmd_unrelated_enabled": "📦 Nhận tin không liên quan: BẬT. Bản tin sẽ điền thêm tin tức tổng hợp nếu thiếu tin liên quan.",
        "cmd_unrelated_disabled": "🚫 Nhận tin không liên quan: TẮT. Bản tin sẽ chỉ chứa đúng các chủ đề bạn theo dõi.",
        "cmd_unrelated_invalid": "⚠️ Cú pháp không hợp lệ. Vui lòng sử dụng: /unrelated [yes/no]",
        
        # AI Prompts (Action-oriented)
        "prompt_summarizer": (
            "Nhiệm vụ: Tóm tắt nội dung sau đây một cách khách quan trong CHÍNH XÁC 1 hoặc 2 câu ngắn gọn, thực tế. "
            "Yêu cầu: KHÔNG thêm phân tích, ý kiến cá nhân hoặc các cụm từ dẫn nhập. "
            "Ngôn ngữ: Trả lời bằng tiếng Việt.\n\n"
            "Nội dung: {content}"
        ),
        "prompt_query_designer": (
            "Nhiệm vụ: Trích xuất 1 từ khóa hoặc 1 cụm từ khóa quan trọng nhất từ yêu cầu của người dùng để phục vụ tìm kiếm.\n"
            "Ràng buộc:\n"
            "- không thêm bất kỳ văn bản, nhãn hoặc giải thích nào khác.\n"
            "- Giữ nguyên tên riêng, tên sản phẩm, tên công ty, địa danh và thuật ngữ chuyên ngành.\n"
            "- Loại bỏ các từ không mang giá trị tìm kiếm như đại từ, trợ từ, từ nối và động từ chung chung.\n"
            "- Ưu tiên các thực thể (entity) và khái niệm thể hiện rõ ý định tìm kiếm.\n"
            "- CHỈ giữ thông tin thời gian (năm, tháng, quý...) khi nó là một phần quan trọng của yêu cầu.\n"
            "- KHÔNG sử dụng toán tử tìm kiếm (site:, OR, dấu ngoặc kép, dấu +, dấu -).\n"
            "Yêu cầu: {user_prompt}"
        ),
        "prompt_synthesizer": (
            "Nhiệm vụ: Trả lời câu hỏi dựa trên các bài báo được cung cấp. "
            "Ràng buộc: CHỈ sử dụng thông tin trong bài báo. Đóng vai trò là 'đôi mắt và đôi tai' (chỉ báo cáo thực tế, không bình luận). "
            "Nếu thiếu thông tin, hãy trả lời 'Tôi không có đủ thông tin từ các bài báo được cung cấp.' "
            "Ngôn ngữ: Trả lời bằng tiếng Việt.\n\n"
            "Các bài báo:\n{articles}\n\n"
            "Câu hỏi: {question}"
        ),
        "prompt_feed_selector": (
            "Task: Select which news categories are highly related, matching, or contextually relevant to a user followed keyword.\n"
            "Constraints:\n"
            "- Analyze the keyword: '{keyword}'\n"
            "- Below is the JSON mapping of publishers and their exact category keys:\n{categories_json}\n"
            "- Return ONLY a valid JSON object mapping publisher names to lists of selected category keys.\n"
            "- Do NOT include any markdown code blocks, explanation, or preamble. Return ONLY the raw JSON string.\n\n"
            "Example output format:\n"
            "{{\n"
            "  \"VnExpress\": [\"so-hoa\"],\n"
            "  \"Tuổi Trẻ\": [\"nhip-song-so\"]\n"
            "}}\n"
        )
    },
    "en": {
        # UI
        "briefing_header": "📅 *DAILY BRIEFING*",
        "details_button": "🔍 Details for item {i}",
        "settings_button": "⚙️ Settings",
        "source_label": "Source",
        "sources_header": "📖 *REFERENCES:*",
        "source_link_text": "Source {i}",
        "end_topic_button": "🔚 End this topic",
        "no_news_found": "No new news found for your briefing.",
        "error_system": "⚠️ A system error occurred while generating your briefing.",
        "error_context_not_found": "Sorry, I can't find the original article context.",
        "error_deep_dive": "⚠️ Error processing your deep-dive request.",
        "focus_mode_entered": "🔍 You are now in Focus Mode. Ask questions about this article, or press the exit button.",
        "focus_mode_exited": "✅ Exited Focus Mode.",
        "ad_hoc_searching": "🔍 Searching the web for your request...",
        "settings_not_implemented": "🚧 Settings feature is under development.",
        "desc_start": "Start onboarding",
        "desc_follow": "Follow a keyword",
        "desc_block": "Block a keyword",
        "desc_unrelated": "Toggle unrelated news",
        "desc_list": "View configuration",
        "desc_brief": "Generate instant briefing",
        "desc_unfollow": "Unfollow a keyword",
        "desc_unblock": "Unblock a keyword",
        "desc_lang": "Change display language",
        "lang_updated": "🌐 Language has been updated to English.",
        
        # Onboarding
        "onboarding_choose_language": "🌐 Chọn ngôn ngữ / Choose your language:",
        "onboarding_welcome": "✅ Hello! I'm News Agent Bot.\n\n📰 I'll automatically send you news briefings at {times}.\n🔍 When you receive a briefing, tap any button to dive deeper.\n\nUse /follow <keyword> to track topics, /block <keyword> to block, /list to view config.",
        
        # Commands
        "cmd_brief_triggering": "⏳ Generating an instant briefing for you...",
        "cmd_follow_added": "✅ Follow keyword added: {keyword}",
        "cmd_block_added": "🚫 Block keyword added: {keyword}",
        "cmd_follow_removed": "✅ Follow keyword removed: {keyword}",
        "cmd_block_removed": "✅ Block keyword removed: {keyword}",
        "cmd_keyword_not_found": "Keyword not found: {keyword}",
        "cmd_missing_keyword": "Please provide a keyword. Example: /follow AI",
        "cmd_list_header": "⚙️ Your configuration:\n\n📌 Following: {follow}\n🚫 Blocking: {block}\n⏰ Briefing times: {times}\n🌐 Language: {language}\n📦 Receive unrelated news: {unrelated}\n📡 Customized feeds count: {custom_feeds_count}",
        "cmd_user_not_found": "You haven't registered yet. Send /start to begin.",
        "cmd_unrelated_enabled": "📦 Receive unrelated news: ON. The briefing will append general fallback news if matched topics are low.",
        "cmd_unrelated_disabled": "🚫 Receive unrelated news: OFF. The briefing will strictly contain your followed topics.",
        "cmd_unrelated_invalid": "⚠️ Invalid syntax. Please use: /unrelated [yes/no]",
        
        # AI Prompts (Action-oriented)
        "prompt_summarizer": (
            "Task: Summarize the following content objectively in EXACTLY 1 or 2 concise, factual sentences. "
            "Constraint: Do NOT add any analysis, opinion, or introductory phrases. "
            "Language: Respond in English.\n\n"
            "Content: {content}"
        ),
        "prompt_query_designer": (
            "Task: Extract the single most important keyword or keyphrase from the user's request for search purposes.\n"
            "Constraints:\n"
            "- Do not add any other text, labels, or explanations.\n"
            "- Preserve proper nouns, product names, company names, locations, and technical terms.\n"
            "- Remove non-search-value words such as pronouns, particles, conjunctions, and generic verbs.\n"
            "- Prioritize entities and concepts that clearly reflect the search intent.\n"
            "- ONLY keep time information (year, month, quarter...) if it is a crucial part of the request.\n"
            "- DO NOT use search operators (site:, OR, quotation marks, +, -).\n"
            "Request: {user_prompt}"
        ),
        "prompt_synthesizer": (
            "Task: Answer the question based on the provided articles. "
            "Constraint: Use ONLY the provided articles. Act as 'eyes and ears' (report facts only, no bias or opinion). "
            "If information is missing, respond 'I don't have enough information from the provided articles.' "
            "Language: Respond in English.\n\n"
            "Articles:\n{articles}\n\n"
            "Question: {question}"
        ),
        "prompt_feed_selector": (
            "Task: Select which news categories are highly related, matching, or contextually relevant to a user followed keyword.\n"
            "Constraints:\n"
            "- Analyze the keyword: '{keyword}'\n"
            "- Below is the JSON mapping of publishers and their exact category keys:\n{categories_json}\n"
            "- Return ONLY a valid JSON object mapping publisher names to lists of selected category keys.\n"
            "- Do NOT include any markdown code blocks, explanation, or preamble. Return ONLY the raw JSON string.\n\n"
            "Example output format:\n"
            "{{\n"
            "  \"VnExpress\": [\"so-hoa\"],\n"
            "  \"Tuổi Trẻ\": [\"nhip-song-so\"]\n"
            "}}\n"
        )
    }
}

def get_text(key: str, lang: str = "vi", **kwargs: Any) -> str:
    """
    Retrieve a localized string or template by key and language.
    """
    lang_dict = I18N.get(lang, I18N["vi"])
    template = lang_dict.get(key, lang_dict.get(key, I18N["vi"].get(key, key)))
    
    try:
        if kwargs:
            return template.format(**kwargs)
        return template
    except (KeyError, IndexError):
        return template
