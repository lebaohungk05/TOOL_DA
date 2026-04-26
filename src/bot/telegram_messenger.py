import logging
from typing import Any
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

from src.models import NewsDTO
from src.bot.protocol import MessengerProtocol
from src.core.i18n import get_text
import datetime

logger = logging.getLogger(__name__)

class TelegramFormatter:
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

    def format_briefing(self, news_items: list[NewsDTO], language: str = "vi") -> str:
        """
        Formats a list of news items into a single rich-text vertical briefing.
        
        Args:
            news_items: List of articles to include.
            language: Target language for labels.
            
        Returns:
            A string formatted in Telegram MarkdownV2.
        """
        now = datetime.datetime.now()
        localized_header = get_text("briefing_header", language)
        header = f"{localized_header} \\- {now.strftime('%H:%M')} \\- {now.strftime('%d/%m/%Y')}\n\n"
        
        source_label = get_text("source_label", language)
        
        body = ""
        for i, item in enumerate(news_items, 1):
            title = self._escape(item.title)
            summary = self._escape(item.summary)
            source = self._escape(item.source)
            
            body += f"{i}\\. *{title}*\n"
            body += f"   {summary}\n"
            body += f"   _{source_label}: {source}_\n\n"
            
        return header + body

    def format_deep_dive(self, answer: str, sources: list[str], language: str = "vi") -> str:
        """
        Formats a detailed AI response with clickable source links.
        
        Args:
            answer: The main text response from the AI.
            sources: A list of URL strings.
            language: Target language for labels.
            
        Returns:
            A string formatted in Telegram MarkdownV2.
        """
        # We escape the answer carefully. Note: LLM might generate some markdown 
        # that we might want to preserve, but for safety in V2 we escape everything 
        # unless we implement a smarter parser.
        escaped_answer = self._escape(answer)
        
        localized_header = get_text("sources_header", language)
        sources_section = f"\n\n{localized_header}\n"
        
        link_label_template = get_text("source_link_text", language)
        
        for i, url in enumerate(sources, 1):
            escaped_url = self._escape(url)
            link_text = link_label_template.format(i=i)
            sources_section += f"{i}\\. [{link_text}]({escaped_url})\n"
            
        return escaped_answer + sources_section


class TelegramMessenger(MessengerProtocol):
    """
    Implementation of MessengerProtocol using the aiogram library.
    Handles the delivery of formatted messages and interactive components to Telegram.
    """

    def __init__(self, bot: Bot):
        """
        Initialize the messenger with a bot instance.
        
        Args:
            bot: The aiogram Bot instance.
        """
        self.bot = bot
        self.formatter = TelegramFormatter()

    async def send_briefing(self, recipient_id: str, news_items: list[NewsDTO], language: str = "vi") -> None:
        """
        Send a formatted daily briefing with interactive deep-dive buttons.
        
        Args:
            recipient_id: The unique ID of the recipient.
            news_items: The list of articles to include in the briefing.
            language: The user's preferred language.
        """
        try:
            chat_id = int(recipient_id)
            text = self.formatter.format_briefing(news_items, language)
            
            builder = InlineKeyboardBuilder()
            
            button_template = get_text("details_button", language)
            # Create a button for each news item
            for i, item in enumerate(news_items, 1):
                builder.button(
                    text=button_template.format(i=i),
                    callback_data=f"deep_dive:{item.article_id}"
                )
            
            # Add a settings button at the bottom
            builder.button(
                text=get_text("settings_button", language),
                callback_data="settings"
            )
            
            # Adjust the layout: 1 button per row for clarity
            builder.adjust(1)
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=builder.as_markup()
            )
            logger.info(f"Briefing sent to chat {chat_id} in {language}")
            
        except Exception as e:
            logger.error(f"Failed to send briefing to {recipient_id}: {str(e)}")
            raise

    async def send_deep_dive_response(self, recipient_id: str, text: str, sources: list[str], language: str = "vi") -> None:
        """
        Send a detailed AI response with source links and an exit button.
        
        Args:
            recipient_id: The unique ID of the recipient.
            text: The main response body from the AI.
            sources: List of source URLs.
            language: The user's preferred language.
        """
        try:
            chat_id = int(recipient_id)
            formatted_text = self.formatter.format_deep_dive(text, sources, language)
            
            builder = InlineKeyboardBuilder()
            builder.button(
                text=get_text("end_topic_button", language), 
                callback_data="exit_focus"
            )
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=formatted_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=builder.as_markup()
            )
            logger.info(f"Deep-dive response sent to chat {chat_id} in {language}")
            
        except Exception as e:
            logger.error(f"Failed to send deep-dive to {recipient_id}: {str(e)}")
            raise

    async def notify_event(self, recipient_id: str, message_key: str, **kwargs: Any) -> None:
        """
        Send system notifications or error messages using localized keys.
        
        Args:
            recipient_id: The unique ID of the recipient.
            message_key: The i18n key for the message.
            **kwargs: Additional formatting arguments for the localized string.
        """
        try:
            chat_id = int(recipient_id)
            language = kwargs.get("language", "vi")
            
            # If message_key is in I18N, use it, otherwise use it as raw text
            text = get_text(message_key, language, **kwargs)
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=text
            )
            logger.info(f"System notification sent to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Failed to send notification to {recipient_id}: {str(e)}")
