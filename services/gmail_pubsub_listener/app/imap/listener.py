"""Background IMAP listener maintaining persistent IDLE connection."""
import asyncio
import logging
from typing import Optional
from app.config import get_settings
from app.imap.client import GmailIMAPClient
from app.imap.reconnect import BackoffStrategy
from app.imap.synchronizer import MailboxSynchronizer
from app.persistence.repository import Repository, repository as default_repo

logger = logging.getLogger(__name__)


class IMAPListener:
    def __init__(
        self,
        client: Optional[GmailIMAPClient] = None,
        synchronizer: Optional[MailboxSynchronizer] = None,
        repo: Optional[Repository] = None,
    ):
        self.settings = get_settings()
        self.client = client or GmailIMAPClient()
        self.repo = repo or default_repo
        self.synchronizer = synchronizer or MailboxSynchronizer(self.client, self.repo)
        self.backoff = BackoffStrategy(initial=1.0, multiplier=2.0, max_delay=60.0)
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._mailbox = self.settings.IMAP_MAILBOX

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self) -> None:
        """Starts the IMAP listener background loop."""
        if self._running:
            logger.warning("IMAPListener is already running.")
            return

        if not self.settings.GMAIL_ADDRESS or not self.settings.GMAIL_APP_PASSWORD:
            logger.info("Gmail credentials not fully configured. IMAPListener waiting in dormant state.")
            return

        self._running = True
        self._task = asyncio.create_task(self._listen_loop())
        logger.info(f"IMAPListener started for mailbox '{self._mailbox}'.")

    async def stop(self) -> None:
        """Gracefully stops the listener and closes IMAP connection."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await asyncio.to_thread(self.client.close)
        await self.repo.update_mailbox_state(self._mailbox, last_uid=0, status="STOPPED")
        logger.info("IMAPListener stopped.")

    async def _listen_loop(self) -> None:
        while self._running:
            try:
                # 1. Connect and Authenticate
                logger.info("Connecting to Gmail IMAP...")
                await asyncio.to_thread(self.client.connect)
                await asyncio.to_thread(self.client.authenticate)
                await asyncio.to_thread(self.client.select_mailbox, self._mailbox)
                self.backoff.reset()
                logger.info(f"Connected and authenticated on mailbox '{self._mailbox}'.")

                # 2. Sync any messages arrived while offline
                await self.repo.update_mailbox_state(self._mailbox, last_uid=0, status="SYNCING")
                await self.synchronizer.sync_mailbox(self._mailbox)
                await self.repo.update_mailbox_state(self._mailbox, last_uid=0, status="IDLE")

                # 3. IDLE Loop
                while self._running and self.client.is_connected:
                    # Enter IDLE in worker thread
                    logger.info("Entering IMAP IDLE state...")
                    has_exists = await asyncio.to_thread(
                        self.client.idle_wait, self.settings.IDLE_DURATION_SECONDS
                    )

                    if not self._running:
                        break

                    if has_exists:
                        logger.info("EXISTS notification received! Synchronizing new messages...")
                        await self.repo.update_mailbox_state(self._mailbox, last_uid=0, status="SYNCING")
                        await self.synchronizer.sync_mailbox(self._mailbox)
                        await self.repo.update_mailbox_state(self._mailbox, last_uid=0, status="IDLE")
                    else:
                        logger.info("IDLE cycle duration reached. Refreshing IDLE connection...")
                        # Run a quick sync check on timeout
                        await self.synchronizer.sync_mailbox(self._mailbox)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"IMAP connection error: {e}", exc_info=False)
                await asyncio.to_thread(self.client.close)
                if self._running:
                    await self.backoff.wait()


imap_listener = IMAPListener()
