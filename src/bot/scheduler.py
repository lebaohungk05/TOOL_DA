import logging
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.services.protocol import BriefingServiceProtocol
from src.database.protocol import StorageProtocol

logger = logging.getLogger(__name__)


class BriefingScheduler:
    """
    Inbound Adapter that uses APScheduler to trigger scheduled briefings.
    Checks every minute whether any user's configured briefing_times
    match the current time, and dispatches briefings accordingly.
    """

    def __init__(
        self,
        briefing_service: BriefingServiceProtocol,
        storage: StorageProtocol,
    ) -> None:
        """
        Initialize the scheduler with required protocols.

        Args:
            briefing_service: The orchestrator for the briefing workflow.
            storage: Persistence layer to enumerate user configurations.
        """
        self.briefing_service = briefing_service
        self.storage = storage
        self._scheduler = AsyncIOScheduler()

    async def start(self) -> None:
        """Start the scheduler with 1-minute interval checks."""
        self._scheduler.add_job(
            self._check_and_dispatch,
            trigger=IntervalTrigger(minutes=1),
            id="briefing_check",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info("BriefingScheduler started (1-minute interval)")

    async def stop(self) -> None:
        """Shut down the scheduler gracefully."""
        self._scheduler.shutdown(wait=False)
        logger.info("BriefingScheduler stopped")

    async def _check_and_dispatch(self) -> None:
        """
        Tick function: compare current HH:MM against each user's
        briefing_times and dispatch briefings for matching users.
        """
        current_time = datetime.datetime.now().strftime("%H:%M")
        logger.debug(f"Scheduler tick at {current_time}")

        try:
            all_configs = await self.storage.get_all_user_configs()
        except Exception as e:
            logger.error(f"Failed to fetch user configs for scheduling: {e}")
            return

        for config in all_configs:
            if current_time in config.briefing_times:
                logger.info(
                    f"Dispatching scheduled briefing for {config.recipient_id} "
                    f"at {current_time}"
                )
                try:
                    await self.briefing_service.run_scheduled_briefing(
                        config.recipient_id
                    )
                except Exception as e:
                    logger.error(
                        f"Scheduled briefing failed for {config.recipient_id}: {e}"
                    )
