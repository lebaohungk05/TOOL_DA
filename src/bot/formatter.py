import datetime

from src.models import NewsDTO
from src.bot.protocol import FormatterProtocol

class TelegramFormatter(FormatterProtocol):
    """
    Formatter for Telegram MarkdownV2 messages.
    Ensures all dynamic content is properly escaped to avoid delivery failures.
    """

    def _escape(self, text: str) -> str:
        """
        Escapes Telegram MarkdownV2 special characters.
        
        Args:
            text: The raw text to escape.
            
        Returns:
            The escaped string safe for MarkdownV2.
        """
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return "".join(f"\\{c}" if c in escape_chars else c for c in text)

    def format_briefing(self, news_items: list[NewsDTO]) -> str:
        """
        Formats a list of news items into a single rich-text vertical briefing.
        
        Args:
            news_items: List of articles to include.
            
        Returns:
            A string formatted in Telegram MarkdownV2.
        """
        now = datetime.datetime.now()
        header = f"*BẢN TIN ĐỊNH KỲ* \\- {now.strftime('%H:%M')} \\- {now.strftime('%d/%m/%Y')}\n\n"
        
        body = ""
        for i, item in enumerate(news_items, 1):
            title = self._escape(item.title)
            summary = self._escape(item.summary)
            source = self._escape(item.source)
            
            body += f"{i}\\. *{title}*\n"
            body += f"   {summary}\n"
            body += f"   _Nguồn: {source}_\n\n"
            
        return header + body

    def format_deep_dive(self, answer: str, sources: list[str]) -> str:
        """
        Formats a detailed AI response with clickable source links.
        
        Args:
            answer: The main text response from the AI.
            sources: A list of URL strings.
            
        Returns:
            A string formatted in Telegram MarkdownV2.
        """
        escaped_answer = self._escape(answer)
        
        sources_section = "\n\n*CÁC NGUỒN THAM KHẢO:*\n"
        for i, url in enumerate(sources, 1):
            escaped_url = self._escape(url)
            # Markdown link: [text](url)
            sources_section += f"{i}\\. [Nguồn {i}]({escaped_url})\n"
            
        return escaped_answer + sources_section
