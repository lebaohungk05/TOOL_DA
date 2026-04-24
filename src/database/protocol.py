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

    async def upsert_user_config(self, user_id: int, config: UserConfigDTO) -> None:
        """
        Save or update user configuration.
        
        Args:
            user_id: The unique Telegram user ID.
            config: The configuration DTO.
        """
        ...

    async def get_user_config(self, user_id: int) -> Optional[UserConfigDTO]:
        """
        Retrieve user configuration by ID.
        
        Args:
            user_id: The unique Telegram user ID.
            
        Returns:
            The UserConfigDTO if found, else None.
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
