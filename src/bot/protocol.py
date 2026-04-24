from typing import Protocol
from src.models import NewsDTO

class FormatterProtocol(Protocol):
    """Protocol for formatting news data into various string formats."""

    def format_briefing(self, news_items: list[NewsDTO]) -> str:
        """Convert a list of news items into rich-text Telegram message content."""
        ...

    def format_deep_dive(self, answer: str, sources: list[str]) -> str:
        """Format an AI response with transparent source links."""
        ...

class MessengerProtocol(Protocol):
    """Protocol for sending messages to users via various platforms."""

    async def send_briefing(self, chat_id: int, news_items: list[NewsDTO]) -> None:
        """Send a summary briefing with navigation buttons."""
        ...

    async def send_deep_dive_response(self, chat_id: int, text: str, sources: list[str]) -> None:
        """Send a detailed response for a deep-dive request, including references."""
        ...

    async def notify_system_event(self, chat_id: int, message: str) -> None:
        """Send system notifications (configuration confirmation, errors)."""
        ...
