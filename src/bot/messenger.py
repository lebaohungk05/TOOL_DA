import logging
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

from src.models import NewsDTO
from src.bot.protocol import MessengerProtocol, FormatterProtocol

logger = logging.getLogger(__name__)

class TelegramMessenger(MessengerProtocol):
    """
    Implementation of MessengerProtocol using the aiogram library.
    Handles the delivery of formatted messages and interactive components to Telegram.
    """

    def __init__(self, bot: Bot, formatter: FormatterProtocol):
        """
        Initialize the messenger with a bot instance and a formatter.
        
        Args:
            bot: The aiogram Bot instance.
            formatter: An implementation of FormatterProtocol.
        """
        self.bot = bot
        self.formatter = formatter

    async def send_briefing(self, chat_id: int, news_items: list[NewsDTO]) -> None:
        """
        Send a formatted daily briefing with interactive deep-dive buttons.
        
        Args:
            chat_id: The Telegram chat ID to send to.
            news_items: The list of articles to include in the briefing.
        """
        try:
            text = self.formatter.format_briefing(news_items)
            
            builder = InlineKeyboardBuilder()
            # Create a button for each news item
            for i, item in enumerate(news_items, 1):
                builder.button(
                    text=f"🔍 Details for item {i}",
                    callback_data=f"deep_dive:{item.article_id}"
                )
            
            # Add a settings button at the bottom
            builder.button(text="⚙️ Settings", callback_data="settings")
            
            # Adjust the layout: 1 button per row for clarity
            builder.adjust(1)
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=builder.as_markup()
            )
            logger.info(f"Briefing sent to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Failed to send briefing to {chat_id}: {str(e)}")
            raise

    async def send_deep_dive_response(self, chat_id: int, text: str, sources: list[str]) -> None:
        """
        Send a detailed AI response with source links and an exit button.
        
        Args:
            chat_id: The Telegram chat ID.
            text: The main response body from the AI.
            sources: List of source URLs.
        """
        try:
            formatted_text = self.formatter.format_deep_dive(text, sources)
            
            builder = InlineKeyboardBuilder()
            builder.button(text="🔚 End this topic", callback_data="exit_focus")
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=formatted_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=builder.as_markup()
            )
            logger.info(f"Deep-dive response sent to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Failed to send deep-dive to {chat_id}: {str(e)}")
            raise

    async def notify_system_event(self, chat_id: int, message: str) -> None:
        """
        Send system notifications or error messages.
        
        Args:
            chat_id: The Telegram chat ID.
            message: The notification text.
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            logger.info(f"System notification sent to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Failed to send notification to {chat_id}: {str(e)}")
