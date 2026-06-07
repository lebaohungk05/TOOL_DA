import logging
from typing import Any

from src.models import UserConfigDTO
from src.services.protocol import AgentControllerProtocol, BriefingServiceProtocol
from src.database.protocol import StorageProtocol
from src.bot.protocol import MessengerProtocol
from src.news.sources import PUBLISHERS, resolve_category_to_url

logger = logging.getLogger(__name__)

# Default briefing schedule for new users
DEFAULT_BRIEFING_TIMES = ["08:00", "20:00"]


class AgentController(AgentControllerProtocol):
    """
    Concrete implementation of the Inbound Port.
    Routes external signals (user commands, interactions) to the appropriate
    Core use case (BriefingService) and manages session context (Focus Mode,
    onboarding) via StorageProtocol.

    This is a Core component — no platform-specific imports (aiogram, etc.) allowed.
    """

    def __init__(
        self,
        briefing_service: BriefingServiceProtocol,
        storage: StorageProtocol,
        messenger: MessengerProtocol,
    ) -> None:
        """
        Initialize the controller with required protocols.

        Args:
            briefing_service: The orchestrator for briefing and deep-dive workflows.
            storage: Persistence layer for user configs and session context.
            messenger: Outbound port for sending messages to users.
        """
        self.briefing_service = briefing_service
        self.storage = storage
        self.messenger = messenger

    async def handle_user_command(self, recipient_id: str, text: str) -> None:
        """
        Process a free-text message or command from a user.

        Priority order:
        1. /start command → trigger onboarding (handled by Telegram handler directly)
        2. Commands: /follow, /block, /list
        3. Focus Mode → deep-dive question
        4. Fallback → ad-hoc stub

        Args:
            recipient_id: The unique recipient identifier.
            text: The raw text message from the user.
        """
        logger.info(f"Handling command from {recipient_id}: {text[:80]}")
        stripped = text.strip()

        # 1. Check onboarding state
        session = await self.storage.get_session_context(recipient_id)

        # 2. Parse commands
        lower = stripped.lower()
        if lower.startswith("/follow"):
            await self._handle_follow(recipient_id, stripped)
            return
        if lower.startswith("/unfollow"):
            await self._handle_unfollow(recipient_id, stripped)
            return
        if lower.startswith("/block"):
            await self._handle_block(recipient_id, stripped)
            return
        if lower.startswith("/unblock"):
            await self._handle_unblock(recipient_id, stripped)
            return
        if lower.startswith("/unrelated"):
            await self._handle_unrelated(recipient_id, stripped)
            return
        if lower == "/list":
            await self._handle_list(recipient_id)
            return
        if lower == "/brief":
            await self._handle_brief(recipient_id)
            return
        if lower == "/lang":
            await self._handle_lang(recipient_id)
            return

        # 3. Check Focus Mode
        focus_article_id = session.get("focus_article_id") if session else None
        if focus_article_id:
            await self.briefing_service.run_deep_dive(
                recipient_id, focus_article_id, stripped
            )
            return

        # 4. Fallback: Ad-hoc free search
        await self.briefing_service.run_ad_hoc_query(recipient_id, stripped)

    async def handle_interaction(
        self, recipient_id: str, action_id: str, payload: dict[str, Any]
    ) -> None:
        """
        Process a structured interaction (callback button, menu click).

        Supported action_ids:
        - "select_language": User chose a language during onboarding.
        - "deep_dive": Enter Focus Mode for a specific article.
        - "exit_focus": Leave Focus Mode.
        - "settings": Placeholder for future settings UI.

        Args:
            recipient_id: The unique recipient identifier.
            action_id: The action identifier string.
            payload: Additional data attached to the action.
        """
        logger.info(f"Handling interaction from {recipient_id}: {action_id}")

        if action_id == "select_language":
            language: str = payload.get("language", "vi")
            await self._complete_onboarding(recipient_id, language)

        elif action_id == "update_language":
            language: str = payload.get("language", "vi")
            await self._update_language(recipient_id, language)

        elif action_id == "deep_dive":
            article_id: str = payload.get("article_id", "")
            if not article_id:
                logger.warning(f"deep_dive missing article_id from {recipient_id}")
                return
            await self.storage.save_session_context(
                recipient_id, {"focus_article_id": article_id}
            )
            # Determine user language
            lang = await self._get_user_language(recipient_id)
            await self.messenger.notify_event(
                recipient_id, "focus_mode_entered", language=lang
            )

        elif action_id == "exit_focus":
            await self.storage.save_session_context(recipient_id, {})
            lang = await self._get_user_language(recipient_id)
            await self.messenger.notify_event(
                recipient_id, "focus_mode_exited", language=lang
            )

        elif action_id == "settings":
            lang = await self._get_user_language(recipient_id)
            await self.messenger.notify_event(
                recipient_id, "settings_not_implemented", language=lang
            )

        else:
            logger.warning(f"Unrecognized action_id '{action_id}' from {recipient_id}")

    # --- Private helpers ---

    async def _get_user_language(self, recipient_id: str) -> str:
        """Retrieve the user's configured language, default to 'vi'."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        return config.language if config else "vi"

    async def _complete_onboarding(
        self, recipient_id: str, language: str
    ) -> None:
        """
        Finalize onboarding: save UserConfig with defaults, clear session,
        send welcome message.

        Args:
            recipient_id: The unique recipient identifier.
            language: The user's selected language.
        """
        times_str = ", ".join(DEFAULT_BRIEFING_TIMES)

        config = UserConfigDTO(
            user_id=recipient_id,
            recipient_id=recipient_id,
            follow_keywords=[],
            block_keywords=[],
            name="",
            briefing_times=list(DEFAULT_BRIEFING_TIMES),
            language=language,
            custom_feeds={}
        )
        await self.storage.upsert_user_config(user_id=recipient_id, config=config)

        # Clear onboarding session
        await self.storage.save_session_context(recipient_id, {})

        # Send welcome
        await self.messenger.notify_event(
            recipient_id,
            "onboarding_welcome",
            language=language,
            times=times_str,
        )
        logger.info(f"Onboarding complete for {recipient_id} (lang={language})")

    async def _handle_follow(self, recipient_id: str, text: str) -> None:
        """Parse /follow command, trigger LLM feed routing, and save customized URLs."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            await self.messenger.notify_event(recipient_id, "cmd_user_not_found")
            return

        keyword = text[len("/follow"):].strip()
        if not keyword:
            await self.messenger.notify_event(
                recipient_id, "cmd_missing_keyword", language=config.language
            )
            return

        updated_follow = list(config.follow_keywords)
        if keyword not in updated_follow:
            updated_follow.append(keyword)

        # Trigger dynamic LLM feed routing
        categories_dict = {pub: info["categories"] for pub, info in PUBLISHERS.items()}
        logger.info(f"Triggering LLM feed selection for keyword '{keyword}' across categories.")
        
        selected_feeds = await self.briefing_service.ai_service.select_related_feeds(
            keyword, categories_dict, config.language
        )
        
        resolved_urls = []
        for pub, cats in selected_feeds.items():
            for cat in cats:
                try:
                    url = resolve_category_to_url(pub, cat)
                    resolved_urls.append(url)
                except Exception as e:
                    logger.warning(f"Failed to resolve matched feed {pub}/{cat}: {e}")
                    
        # Update custom feeds map for this keyword
        existing_feeds = getattr(config, "custom_feeds", {})
        updated_feeds = dict(existing_feeds)
        updated_feeds[keyword] = resolved_urls
        logger.info(f"Follow: Resolved {len(resolved_urls)} feed URLs for '{keyword}'. Total tracked keywords: {len(updated_feeds)}")

        updated = UserConfigDTO(
            user_id=config.user_id,
            recipient_id=config.recipient_id,
            follow_keywords=updated_follow,
            block_keywords=list(config.block_keywords),
            name=config.name,
            briefing_times=list(config.briefing_times),
            language=config.language,
            allow_unrelated=getattr(config, "allow_unrelated", True),
            custom_feeds=updated_feeds
        )
        await self.storage.upsert_user_config(user_id=recipient_id, config=updated)
        await self.messenger.notify_event(
            recipient_id, "cmd_follow_added", language=config.language, keyword=keyword
        )

    async def _handle_block(self, recipient_id: str, text: str) -> None:
        """Parse /block command and add keyword to user config."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            await self.messenger.notify_event(recipient_id, "cmd_user_not_found")
            return

        keyword = text[len("/block"):].strip()
        if not keyword:
            await self.messenger.notify_event(
                recipient_id, "cmd_missing_keyword", language=config.language
            )
            return

        updated_block = list(config.block_keywords)
        if keyword not in updated_block:
            updated_block.append(keyword)

        updated = UserConfigDTO(
            user_id=config.user_id,
            recipient_id=config.recipient_id,
            follow_keywords=list(config.follow_keywords),
            block_keywords=updated_block,
            name=config.name,
            briefing_times=list(config.briefing_times),
            language=config.language,
            allow_unrelated=getattr(config, "allow_unrelated", True),
            custom_feeds=dict(getattr(config, "custom_feeds", {}))
        )
        await self.storage.upsert_user_config(user_id=recipient_id, config=updated)
        await self.messenger.notify_event(
            recipient_id, "cmd_block_added", language=config.language, keyword=keyword
        )

    async def _handle_list(self, recipient_id: str) -> None:
        """Show current user configuration."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            await self.messenger.notify_event(recipient_id, "cmd_user_not_found")
            return

        follow_str = ", ".join(config.follow_keywords) if config.follow_keywords else "—"
        block_str = ", ".join(config.block_keywords) if config.block_keywords else "—"
        times_str = ", ".join(config.briefing_times) if config.briefing_times else "—"
        
        allow_unrelated = getattr(config, "allow_unrelated", True)
        unrelated_str = "Có" if allow_unrelated else "Không"
        
        # Count unique custom feed URLs across all keywords
        all_urls = set()
        for urls in getattr(config, "custom_feeds", {}).values():
            all_urls.update(urls)
        custom_feeds_count = len(all_urls)

        await self.messenger.notify_event(
            recipient_id,
            "cmd_list_header",
            language=config.language,
            follow=follow_str,
            block=block_str,
            times=times_str,
            unrelated=unrelated_str,
            custom_feeds_count=custom_feeds_count,
            language_display=config.language.upper(),
        )

    async def _handle_brief(self, recipient_id: str) -> None:
        """
        Immediately trigger a scheduled briefing for the user.

        Args:
            recipient_id: The unique recipient identifier.
        """
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            await self.messenger.notify_event(recipient_id, "cmd_user_not_found")
            return

        await self.messenger.notify_event(
            recipient_id, "cmd_brief_triggering", language=config.language
        )
        await self.briefing_service.run_scheduled_briefing(recipient_id)

    async def _handle_unrelated(self, recipient_id: str, text: str) -> None:
        """Parse /unrelated command and configure strict curation toggle."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            await self.messenger.notify_event(recipient_id, "cmd_user_not_found")
            return

        arg = text[len("/unrelated"):].strip().lower()
        if arg in ["yes", "y", "true", "on"]:
            val = True
        elif arg in ["no", "n", "false", "off"]:
            val = False
        else:
            await self.messenger.notify_event(
                recipient_id, "cmd_unrelated_invalid", language=config.language
            )
            return

        updated = UserConfigDTO(
            user_id=config.user_id,
            recipient_id=config.recipient_id,
            follow_keywords=list(config.follow_keywords),
            block_keywords=list(config.block_keywords),
            name=config.name,
            briefing_times=list(config.briefing_times),
            language=config.language,
            allow_unrelated=val,
            custom_feeds=dict(getattr(config, "custom_feeds", {}))
        )
        await self.storage.upsert_user_config(user_id=recipient_id, config=updated)
        
        event_key = "cmd_unrelated_enabled" if val else "cmd_unrelated_disabled"
        await self.messenger.notify_event(recipient_id, event_key, language=config.language)

    async def _handle_unfollow(self, recipient_id: str, text: str) -> None:
        """Parse /unfollow command and remove keyword from follow_keywords."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            await self.messenger.notify_event(recipient_id, "cmd_user_not_found")
            return

        keyword = text[len("/unfollow"):].strip()
        if not keyword:
            await self.messenger.notify_event(
                recipient_id, "cmd_missing_keyword", language=config.language
            )
            return

        updated_follow = list(config.follow_keywords)
        if keyword in updated_follow:
            updated_follow.remove(keyword)
            existing_feeds = getattr(config, "custom_feeds", {})
            updated_feeds = dict(existing_feeds)
            updated_feeds.pop(keyword, None)
            
            updated = UserConfigDTO(
                user_id=config.user_id,
                recipient_id=config.recipient_id,
                follow_keywords=updated_follow,
                block_keywords=list(config.block_keywords),
                name=config.name,
                briefing_times=list(config.briefing_times),
                language=config.language,
                allow_unrelated=config.allow_unrelated,
                custom_feeds=updated_feeds
            )
            await self.storage.upsert_user_config(user_id=recipient_id, config=updated)
            await self.messenger.notify_event(
                recipient_id, "cmd_follow_removed", language=config.language, keyword=keyword
            )
        else:
            await self.messenger.notify_event(
                recipient_id, "cmd_keyword_not_found", language=config.language, keyword=keyword
            )

    async def _handle_unblock(self, recipient_id: str, text: str) -> None:
        """Parse /unblock command and remove keyword from block_keywords."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            await self.messenger.notify_event(recipient_id, "cmd_user_not_found")
            return

        keyword = text[len("/unblock"):].strip()
        if not keyword:
            await self.messenger.notify_event(
                recipient_id, "cmd_missing_keyword", language=config.language
            )
            return

        updated_block = list(config.block_keywords)
        if keyword in updated_block:
            updated_block.remove(keyword)
            updated = UserConfigDTO(
                user_id=config.user_id,
                recipient_id=config.recipient_id,
                follow_keywords=list(config.follow_keywords),
                block_keywords=updated_block,
                name=config.name,
                briefing_times=list(config.briefing_times),
                language=config.language,
                allow_unrelated=config.allow_unrelated,
                custom_feeds=dict(getattr(config, "custom_feeds", {}))
            )
            await self.storage.upsert_user_config(user_id=recipient_id, config=updated)
            await self.messenger.notify_event(
                recipient_id, "cmd_block_removed", language=config.language, keyword=keyword
            )
        else:
            await self.messenger.notify_event(
                recipient_id, "cmd_keyword_not_found", language=config.language, keyword=keyword
            )

    async def _handle_lang(self, recipient_id: str) -> None:
        """Parse /lang command and send language selection menu."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            await self.messenger.notify_event(recipient_id, "cmd_user_not_found")
            return
        await self.messenger.send_language_menu(recipient_id, is_update=True, language=config.language)

    async def _update_language(self, recipient_id: str, language: str) -> None:
        """Update the user's language without resetting other configuration."""
        config = await self.storage.get_user_config(user_id=recipient_id)
        if not config:
            return
        updated = UserConfigDTO(
            user_id=config.user_id,
            recipient_id=config.recipient_id,
            follow_keywords=list(config.follow_keywords),
            block_keywords=list(config.block_keywords),
            name=config.name,
            briefing_times=list(config.briefing_times),
            language=language,
            allow_unrelated=config.allow_unrelated,
            custom_feeds=dict(getattr(config, "custom_feeds", {}))
        )
        await self.storage.upsert_user_config(user_id=recipient_id, config=updated)
        await self.messenger.notify_event(recipient_id, "lang_updated", language=language)
