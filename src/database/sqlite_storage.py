import json
import logging
import hashlib
from pathlib import Path
from typing import Optional
import aiosqlite

from src.models import NewsDTO, UserConfigDTO
from src.database.protocol import StorageProtocol

logger = logging.getLogger(__name__)

class SQLiteStorage(StorageProtocol):
    """
    SQLite implementation of the StorageProtocol.
    Maintains a single persistent connection for the application lifecycle.
    """

    def __init__(self, db_path: str = "data/news_agent.db"):
        """
        Initialize the storage with a database path.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path)
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """
        Connect to the database and initialize the schema.
        Creates parent directories if they don't exist.
        """
        if self._connection is not None:
            return

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        
        await self._init_schema()
        logger.info(f"Connected to SQLite database at {self.db_path}")

    async def disconnect(self) -> None:
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Disconnected from SQLite database")

    async def _init_schema(self) -> None:
        """Create tables if they do not exist."""
        if not self._connection:
            raise RuntimeError("Database not connected")

        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                recipient_id TEXT NOT NULL,
                config_json TEXT NOT NULL
            )
        """)

        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                recipient_id TEXT PRIMARY KEY,
                context_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                raw_content TEXT,
                summary TEXT,
                published_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._connection.commit()

    async def upsert_user_config(self, user_id: str, config: UserConfigDTO) -> None:
        """Save or update user configuration."""
        if not self._connection:
            await self.connect()

        config_dict = {
            "follow_keywords": config.follow_keywords,
            "block_keywords": config.block_keywords,
            "briefing_times": config.briefing_times,
            "name": config.name,
            "language": config.language,
        }
        config_json = json.dumps(config_dict)

        await self._connection.execute(
            """
            INSERT INTO users (user_id, recipient_id, config_json)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                recipient_id = excluded.recipient_id,
                config_json = excluded.config_json
            """,
            (user_id, config.recipient_id, config_json)
        )
        await self._connection.commit()

    async def get_user_config(self, user_id: str) -> Optional[UserConfigDTO]:
        """Retrieve user configuration by ID."""
        if not self._connection:
            await self.connect()

        async with self._connection.execute(
            "SELECT recipient_id, config_json FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None

            config_data = json.loads(row["config_json"])
            return UserConfigDTO(
                user_id=user_id,
                recipient_id=row["recipient_id"],
                follow_keywords=config_data.get("follow_keywords", []),
                block_keywords=config_data.get("block_keywords", []),
                name=config_data.get("name", ""),
                briefing_times=config_data.get("briefing_times", []),
                language=config_data.get("language", "vi"),
            )

    async def save_session_context(self, recipient_id: str, context: dict) -> None:
        """Save the session context for a recipient."""
        if not self._connection:
            await self.connect()
            
        context_json = json.dumps(context)
        await self._connection.execute(
            """
            INSERT INTO user_sessions (recipient_id, context_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(recipient_id) DO UPDATE SET
                context_json = excluded.context_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (recipient_id, context_json)
        )
        await self._connection.commit()
        
    async def get_session_context(self, recipient_id: str) -> Optional[dict]:
        """Retrieve the session context for a recipient."""
        if not self._connection:
            await self.connect()

        async with self._connection.execute(
            "SELECT context_json FROM user_sessions WHERE recipient_id = ?",
            (recipient_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None

            return json.loads(row["context_json"])

    async def get_all_user_configs(self) -> list[UserConfigDTO]:
        """Retrieve all user configurations for scheduled operations."""
        if not self._connection:
            await self.connect()

        configs: list[UserConfigDTO] = []
        async with self._connection.execute(
            "SELECT user_id, recipient_id, config_json FROM users"
        ) as cursor:
            async for row in cursor:
                config_data = json.loads(row["config_json"])
                configs.append(UserConfigDTO(
                    user_id=row["user_id"],
                    recipient_id=row["recipient_id"],
                    follow_keywords=config_data.get("follow_keywords", []),
                    block_keywords=config_data.get("block_keywords", []),
                    name=config_data.get("name", ""),
                    briefing_times=config_data.get("briefing_times", []),
                    language=config_data.get("language", "vi"),
                ))
        return configs

    async def archive_news_items(self, items: list[NewsDTO]) -> list[str]:
        """Archive a list of news items and return their unique IDs."""
        if not self._connection:
            await self.connect()

        article_ids = []
        for item in items:
            article_id = item.article_id
            if not article_id:
                # Generate a hash of the URL if ID is not provided
                article_id = hashlib.sha256(item.url.encode()).hexdigest()
            
            article_ids.append(article_id)

            await self._connection.execute(
                """
                INSERT INTO news_articles (article_id, title, url, source, raw_content, summary, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(article_id) DO UPDATE SET
                    summary = CASE WHEN excluded.summary != '' THEN excluded.summary ELSE summary END,
                    raw_content = CASE WHEN excluded.raw_content != '' THEN excluded.raw_content ELSE raw_content END
                """,
                (
                    article_id,
                    item.title,
                    item.url,
                    item.source,
                    item.raw_content,
                    item.summary,
                    item.published_at
                )
            )
        
        await self._connection.commit()
        return article_ids

    async def get_article_by_id(self, article_id: str) -> Optional[NewsDTO]:
        """Retrieve an archived news article by its unique ID."""
        if not self._connection:
            await self.connect()

        async with self._connection.execute(
            "SELECT * FROM news_articles WHERE article_id = ?",
            (article_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None

            return NewsDTO(
                article_id=row["article_id"],
                title=row["title"],
                url=row["url"],
                source=row["source"],
                raw_content=row["raw_content"] or "",
                summary=row["summary"] or "",
                published_at=row["published_at"] or ""
            )
