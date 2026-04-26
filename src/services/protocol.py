from typing import Protocol

class AgentControllerProtocol(Protocol):
    """
    Primary Port: Inbound entry point for all external signals.
    """
    async def handle_user_command(self, recipient_id: str, text: str) -> None:
        """
        Tiếp nhận và xử lý các câu lệnh/tin nhắn văn bản từ người dùng.
        """
        ...

    async def handle_interaction(self, recipient_id: str, action_id: str, payload: dict) -> None:
        """
        Tiếp nhận các tương tác có cấu trúc (callback buttons, menu clicks).
        """
        ...

class BriefingServiceProtocol(Protocol):
    """Protocol for the Briefing Service Orchestrator."""

    async def run_scheduled_briefing(self, recipient_id: str) -> None:
        """
        Execute the full scheduled briefing workflow.
        
        Args:
            recipient_id: The recipient ID to receive the briefing.
        """
        ...

    async def run_deep_dive(self, recipient_id: str, article_id: str, question: str) -> None:
        """
        Execute the contextual deep-dive workflow.
        
        Args:
            recipient_id: The recipient ID.
            article_id: The unique ID of the news article in focus.
            question: The specific question asked by the user.
        """
        ...
