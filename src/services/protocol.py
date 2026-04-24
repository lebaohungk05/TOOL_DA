from typing import Protocol

class BriefingServiceProtocol(Protocol):
    """Protocol for the Briefing Service Orchestrator."""

    async def run_scheduled_briefing(self, chat_id: int) -> None:
        """
        Execute the full scheduled briefing workflow:
        1. Fetch fresh articles.
        2. Filter based on user preferences.
        3. Parallelize AI summarization.
        4. Archive results in the database.
        5. Push formatted briefing to the user.
        
        Args:
            chat_id: The Telegram chat ID to receive the briefing.
        """
        ...

    async def run_deep_dive(self, chat_id: int, article_id: str, question: str) -> None:
        """
        Execute the contextual deep-dive workflow:
        1. Retrieve original article from storage.
        2. Extract search queries using AI.
        3. Fetch additional context via web search.
        4. Synthesize final grounded answer via AI.
        5. Push detailed response to the user.
        
        Args:
            chat_id: The Telegram chat ID.
            article_id: The unique ID of the news article in focus.
            question: The specific question asked by the user.
        """
        ...
