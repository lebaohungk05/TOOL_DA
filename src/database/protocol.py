from typing import Protocol, Optional
from src.models import NewsDTO, UserConfigDTO

class StorageProtocol(Protocol):
    """Protocol for storage implementations."""

    async def connect(self) -> None:
        """Initialize the storage connection and schema."""
        ...

    async def disconnect(self) -> None:
        """Close the storage connection."""
        ...

    async def upsert_user_config(self, user_id: str, config: UserConfigDTO) -> None:
        """
        Save or update user configuration.
        
        Args:
            user_id: The unique user ID.
            config: The configuration DTO.
        """
        ...

    async def get_user_config(self, user_id: str) -> Optional[UserConfigDTO]:
        """
        Retrieve user configuration by ID.
        
        Args:
            user_id: The unique user ID.
            
        Returns:
            The UserConfigDTO if found, else None.
        """
        ...

    async def save_session_context(self, recipient_id: str, context: dict) -> None:
        """
        Save the session context for a recipient.
        
        Args:
            recipient_id: The unique recipient ID.
            context: A dictionary of context data.
        """
        ...
        
    async def get_session_context(self, recipient_id: str) -> Optional[dict]:
        """
        Retrieve the session context for a recipient.
        
        Args:
            recipient_id: The unique recipient ID.
            
        Returns:
            A dictionary of context data if found, else None.
        """
        ...

    async def get_all_user_configs(self) -> list[UserConfigDTO]:
        """
        Retrieve all user configurations.
        Used by the Scheduler to enumerate users for scheduled operations.
        
        Returns:
            A list of all UserConfigDTO entries.
        """
        ...

    async def archive_news_items(self, items: list[NewsDTO]) -> list[str]:
        """
        Archive a list of news items and return their unique IDs.
        
        Args:
            items: List of NewsDTO items to archive.
            
        Returns:
            List of generated or confirmed article_ids.
        """
        ...

    async def get_article_by_id(self, article_id: str) -> Optional[NewsDTO]:
        """
        Retrieve an archived news article by its unique ID.
        
        Args:
            article_id: The unique hash ID of the article.
            
        Returns:
            The NewsDTO if found, else None.
        """
        ...

    async def get_feed_selection_cache(self, keyword: str) -> Optional[dict]:
        """
        Retrieve cached feed selection for a keyword.
        
        Args:
            keyword: The keyword to search cache for.
            
        Returns:
            A dictionary containing 'categories_hash' and 'selected_feeds' if found, else None.
        """
        ...

    async def save_feed_selection_cache(
        self, keyword: str, categories_hash: str, selected_feeds: dict[str, list[str]]
    ) -> None:
        """
        Save feed selection cache for a keyword.
        
        Args:
            keyword: The keyword associated with feed selection.
            categories_hash: Hash of the category dictionary structure.
            selected_feeds: Selected feeds mapping.
        """
        ...

    async def get_delivered_urls(self, user_id: str, within_days: int = 2) -> list[str]:
        """
        Retrieve URLs of articles delivered to the user within specified days.

        Args:
            user_id: The unique user ID.
            within_days: Time window in days.

        Returns:
            A list of delivered article URLs.
        """
        ...

    async def mark_articles_delivered(self, user_id: str, urls: list[str]) -> None:
        """
        Mark a list of article URLs as delivered to the user.

        Args:
            user_id: The unique user ID.
            urls: List of delivered article URLs.
        """
        ...

