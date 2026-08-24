"""
On-Demand Lifecycle Manager for Twenty CRM (Docker Compose).
Automatically spins up Twenty CRM containers when agents/lead finder start work,
and spins them down when work is done while preserving all PostgreSQL persistent volumes.
"""

import asyncio
import logging
import os
import shutil
from contextlib import asynccontextmanager
from typing import Optional

import httpx

from ..config.settings import get_settings

logger = logging.getLogger("TwentyCRMLifecycle")


class TwentyLifecycleManager:
    """
    Manages automated spin-up and spin-down of the local Twenty CRM Docker containers.
    Ensures zero resource consumption when idle while guaranteeing 100% persistent data storage.
    """

    _instance: Optional["TwentyLifecycleManager"] = None

    def __init__(
        self,
        compose_file: str | None = None,
        base_url: str | None = None,
        idle_timeout_seconds: float = 60.0,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.TWENTY_CRM_BASE_URL).rstrip("/")
        self.enabled = settings.TWENTY_CRM_ENABLED
        self.idle_timeout = idle_timeout_seconds

        # Locate docker-compose.twenty.yml in workspace root
        if compose_file:
            self.compose_file = compose_file
        else:
            # Look up relative to project root
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.abspath(os.path.join(curr_dir, "../../../"))
            self.compose_file = os.path.join(root_dir, "docker-compose.twenty.yml")

        self._active_leases = 0
        self._lock = asyncio.Lock()
        self._is_running = False
        self._idle_task: asyncio.Task | None = None

    @classmethod
    def get_instance(cls) -> "TwentyLifecycleManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def is_crm_responsive(self) -> bool:
        """Pings the Twenty CRM endpoint to check if it is active."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/healthz")
                if res.status_code == 200:
                    return True
                res_root = await client.get(f"{self.base_url}/rest/companies")
                return res_root.status_code in (200, 401, 403)
        except Exception:
            return False

    async def spin_up(self, max_wait_seconds: int = 45) -> bool:
        """
        Spins up the Twenty CRM Docker containers if not already active.
        """
        if not self.enabled:
            return False

        async with self._lock:
            # Check if already responsive
            if await self.is_crm_responsive():
                self._is_running = True
                logger.info("Twenty CRM is already responsive and active.")
                return True

            if not os.path.exists(self.compose_file):
                logger.warning(
                    f"Twenty CRM compose file not found at: {self.compose_file}"
                )
                return False

            if not shutil.which("docker"):
                logger.warning(
                    "Docker is not available on this system. Cannot auto-spin up Twenty CRM."
                )
                return False

            logger.info(f"Auto-spinning up Twenty CRM from {self.compose_file}...")
            try:
                proc = await asyncio.create_subprocess_exec(
                    "docker",
                    "compose",
                    "-f",
                    self.compose_file,
                    "up",
                    "-d",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if proc.returncode != 0:
                    logger.warning(f"docker compose up failed: {stderr.decode()}")
                    return False
            except Exception as e:
                logger.warning(f"Error launching docker compose: {e}")
                return False

            # Poll for readiness
            logger.info(
                f"Waiting up to {max_wait_seconds}s for Twenty CRM to become ready..."
            )
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < max_wait_seconds:
                if await self.is_crm_responsive():
                    self._is_running = True
                    logger.info(
                        "Twenty CRM container is now healthy and ready for agent traffic!"
                    )
                    return True
                await asyncio.sleep(2.0)

            logger.warning(
                "Twenty CRM startup timed out (containers may still be initializing)."
            )
            return False

    async def spin_down(self, force: bool = False) -> bool:
        """
        Stops Twenty CRM containers to release RAM/CPU.
        Persistent volumes (PostgreSQL data) remain completely intact on disk.
        """
        if not self.enabled:
            return False

        async with self._lock:
            if self._active_leases > 0 and not force:
                logger.info(
                    f"Twenty CRM has {self._active_leases} active leases. Skipping spin-down."
                )
                return False

            if not os.path.exists(self.compose_file) or not shutil.which("docker"):
                return False

            logger.info(
                "Auto-spinning down Twenty CRM containers (persisting all database data)..."
            )
            try:
                proc = await asyncio.create_subprocess_exec(
                    "docker",
                    "compose",
                    "-f",
                    self.compose_file,
                    "stop",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                self._is_running = False
                logger.info(
                    "Twenty CRM containers stopped successfully. Memory released."
                )
                return proc.returncode == 0
            except Exception as e:
                logger.warning(f"Error stopping docker compose: {e}")
                return False

    @asynccontextmanager
    async def lease(self, auto_spin_down_delay: float | None = None):
        """
        Context manager for agent operations requiring Twenty CRM.
        Spins up CRM on entry, and decrements lease on exit.
        """
        await self.spin_up()
        async with self._lock:
            self._active_leases += 1
            if self._idle_task and not self._idle_task.done():
                self._idle_task.cancel()

        try:
            yield self
        finally:
            async with self._lock:
                self._active_leases = max(0, self._active_leases - 1)

            # Schedule delayed idle shutdown if no leases remain
            delay = (
                auto_spin_down_delay
                if auto_spin_down_delay is not None
                else self.idle_timeout
            )
            if self._active_leases == 0 and delay > 0:
                self._idle_task = asyncio.create_task(
                    self._delayed_idle_shutdown(delay)
                )

    async def _delayed_idle_shutdown(self, delay: float):
        """Waits for idle duration before executing container stop."""
        try:
            await asyncio.sleep(delay)
            if self._active_leases == 0:
                logger.info(
                    f"No active agent activity for {delay}s. Triggering idle spin-down."
                )
                await self.spin_down()
        except asyncio.CancelledError:
            pass
