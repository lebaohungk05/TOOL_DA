from typing import Protocol, Any
from src.models import NewsDTO

class MessengerProtocol(Protocol):
    """Protocol for sending messages to users via various platforms."""

    async def send_briefing(self, recipient_id: str, news_items: list[NewsDTO], language: str = "vi") -> None:
        """Send a summary briefing with navigation buttons."""
        ...

    async def send_deep_dive_response(self, recipient_id: str, text: str, sources: list[str], language: str = "vi") -> None:
        """Send a detailed response for a deep-dive request, including references."""
        ...

    async def notify_event(self, recipient_id: str, message_key: str, **kwargs: Any) -> None:
        """Send system notifications (dùng i18n keys)."""
        ...
