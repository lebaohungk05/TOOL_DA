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
        
        # Onboarding
        "onboarding_choose_language": "🌐 Chọn ngôn ngữ / Choose your language:",
        "onboarding_ask_name": "👋 Chào bạn! Hãy cho tôi biết tên của bạn:",
        "onboarding_welcome": "✅ Xin chào {name}! Tôi là News Agent Bot.\n\n📰 Tôi sẽ tự động gửi bản tin tóm tắt cho bạn vào lúc {times}.\n🔍 Khi nhận bản tin, bạn có thể bấm nút để tìm hiểu sâu hơn.\n\nDùng /follow <từ khóa> để theo dõi chủ đề, /block <từ khóa> để chặn, /list để xem cấu hình.",
        
        # Commands
        "cmd_follow_added": "✅ Đã thêm từ khóa theo dõi: {keyword}",
        "cmd_block_added": "🚫 Đã thêm từ khóa chặn: {keyword}",
        "cmd_follow_removed": "✅ Đã xóa từ khóa theo dõi: {keyword}",
        "cmd_block_removed": "✅ Đã xóa từ khóa chặn: {keyword}",
        "cmd_keyword_not_found": "Không tìm thấy từ khóa: {keyword}",
        "cmd_missing_keyword": "Vui lòng nhập từ khóa. Ví dụ: /follow AI",
        "cmd_list_header": "⚙️ Cấu hình của bạn:\n\n📌 Theo dõi: {follow}\n🚫 Chặn: {block}\n⏰ Giờ nhận tin: {times}\n🌐 Ngôn ngữ: {language}",
        "cmd_user_not_found": "Bạn chưa đăng ký. Hãy gửi /start để bắt đầu.",
        
        # AI Prompts (Action-oriented)
        "prompt_summarizer": (
            "Nhiệm vụ: Tóm tắt nội dung sau đây một cách khách quan trong CHÍNH XÁC 1 hoặc 2 câu ngắn gọn, thực tế. "
            "Yêu cầu: KHÔNG thêm phân tích, ý kiến cá nhân hoặc các cụm từ dẫn nhập. "
            "Ngôn ngữ: Trả lời bằng tiếng Việt.\n\n"
            "Nội dung: {content}"
        ),
        "prompt_query_designer": (
            "Nhiệm vụ: Viết một câu truy vấn tìm kiếm Google duy nhất để tìm câu trả lời cho yêu cầu của người dùng. "
            "Ràng buộc: CHỈ trả về chuỗi tìm kiếm. Không có ngoặc kép, không có văn bản thừa. "
            "Ngôn ngữ: Trả lời bằng tiếng Việt.\n\n"
            "Yêu cầu: {user_prompt}"
        ),
        "prompt_synthesizer": (
            "Nhiệm vụ: Trả lời câu hỏi dựa trên các bài báo được cung cấp. "
            "Ràng buộc: CHỈ sử dụng thông tin trong bài báo. Đóng vai trò là 'đôi mắt và đôi tai' (chỉ báo cáo thực tế, không bình luận). "
            "Nếu thiếu thông tin, hãy trả lời 'Tôi không có đủ thông tin từ các bài báo được cung cấp.' "
            "Ngôn ngữ: Trả lời bằng tiếng Việt.\n\n"
            "Các bài báo:\n{articles}\n\n"
            "Câu hỏi: {question}"
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
        
        # Onboarding
        "onboarding_choose_language": "🌐 Chọn ngôn ngữ / Choose your language:",
        "onboarding_ask_name": "👋 Hello! Please tell me your name:",
        "onboarding_welcome": "✅ Hi {name}! I'm News Agent Bot.\n\n📰 I'll automatically send you news briefings at {times}.\n🔍 When you receive a briefing, tap any button to dive deeper.\n\nUse /follow <keyword> to track topics, /block <keyword> to block, /list to view config.",
        
        # Commands
        "cmd_follow_added": "✅ Follow keyword added: {keyword}",
        "cmd_block_added": "🚫 Block keyword added: {keyword}",
        "cmd_follow_removed": "✅ Follow keyword removed: {keyword}",
        "cmd_block_removed": "✅ Block keyword removed: {keyword}",
        "cmd_keyword_not_found": "Keyword not found: {keyword}",
        "cmd_missing_keyword": "Please provide a keyword. Example: /follow AI",
        "cmd_list_header": "⚙️ Your configuration:\n\n📌 Following: {follow}\n🚫 Blocking: {block}\n⏰ Briefing times: {times}\n🌐 Language: {language}",
        "cmd_user_not_found": "You haven't registered yet. Send /start to begin.",
        
        # AI Prompts (Action-oriented)
        "prompt_summarizer": (
            "Task: Summarize the following content objectively in EXACTLY 1 or 2 concise, factual sentences. "
            "Constraint: Do NOT add any analysis, opinion, or introductory phrases. "
            "Language: Respond in English.\n\n"
            "Content: {content}"
        ),
        "prompt_query_designer": (
            "Task: Write a single Google search query to find news related to the user's request. "
            "Constraint: Return ONLY the search string. No quotes, no prose. "
            "Language: Perform in English.\n\n"
            "Request: {user_prompt}"
        ),
        "prompt_synthesizer": (
            "Task: Answer the question based on the provided articles. "
            "Constraint: Use ONLY the provided articles. Act as 'eyes and ears' (report facts only, no bias or opinion). "
            "If information is missing, respond 'I don't have enough information from the provided articles.' "
            "Language: Respond in English.\n\n"
            "Articles:\n{articles}\n\n"
            "Question: {question}"
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
