"""Production client for Bright Data Scraper Studio (Data Collector) API."""

import asyncio
import json
import os
import shutil
import sys
import time
from typing import Any, Optional

import httpx

from app.brightdata.exceptions import (
    BrightDataAuthError,
    BrightDataConfigError,
    BrightDataError,
    BrightDataJobError,
    BrightDataTimeoutError,
)
from app.config.logging import get_logger
from app.config.settings import Settings, get_settings

logger = get_logger("BRIGHTDATA")

DEFAULT_BASE_URL = "https://api.brightdata.com/dca"

_TERMINAL_COMPLETED_STATUSES = {"ready", "done", "completed"}
_IN_PROGRESS_STATUSES = {"building", "running", "collecting", "pending"}
_FAILURE_STATUSES = {"failed", "error"}


class BrightDataClient:
    """Production client for Bright Data Scraper Studio (Data Collector) API."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 60.0,
    ) -> None:
        self._settings = settings or get_settings()
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    @property
    def api_key(self) -> Optional[str]:
        return self._settings.BRIGHTDATA_API_KEY

    @property
    def collector_id(self) -> Optional[str]:
        return self._settings.BRIGHTDATA_COLLECTOR_ID or self._settings.BRIGHTDATA_DISCOVERY_COLLECTOR_ID

    @property
    def discovery_collector_id(self) -> Optional[str]:
        return self._settings.BRIGHTDATA_DISCOVERY_COLLECTOR_ID or self._settings.BRIGHTDATA_COLLECTOR_ID

    @property
    def company_collector_id(self) -> Optional[str]:
        return self._settings.BRIGHTDATA_COMPANY_COLLECTOR_ID

    @property
    def is_configured(self) -> bool:
        """Return True if Bright Data is enabled in settings and credentials are configured."""
        return bool(self._settings.BRIGHTDATA and self.api_key and (self.collector_id or self.discovery_collector_id))

    def _ensure_configured(self, collector_id: Optional[str] = None) -> tuple[str, str]:
        """Validate credentials and return (api_key, effective_collector_id)."""
        api_key = self.api_key
        effective_collector = collector_id or self.collector_id

        if not api_key or not effective_collector:
            missing: list[str] = []
            if not api_key:
                missing.append("BRIGHTDATA_API_KEY")
            if not effective_collector:
                missing.append("BRIGHTDATA_COLLECTOR_ID")
            msg = f"Bright Data credentials are not configured. Set {', '.join(missing)}."
            logger.error(msg)
            raise BrightDataConfigError(msg)

        return api_key, effective_collector

    @staticmethod
    def _get_headers(api_key: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def trigger_scraper(
        self,
        collector_id: Optional[str] = None,
        inputs: Optional[list[dict[str, Any]]] = None,
    ) -> str:
        """Trigger an asynchronous scraping job on Bright Data Scraper Studio.

        Returns:
            The job_id (collection_id) tracking the run.
        """
        api_key, effective_collector = self._ensure_configured(collector_id)
        endpoint = f"{self._base_url}/trigger"
        params = {"collector": effective_collector}
        payload = inputs or []

        logger.info(f"Triggering collector '{effective_collector}' with {len(payload)} input(s)")

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    endpoint,
                    params=params,
                    json=payload,
                    headers=self._get_headers(api_key),
                )
        except httpx.TimeoutException as error:
            logger.error(f"Timeout while triggering collector {effective_collector}: {error}")
            raise BrightDataTimeoutError(f"Trigger request to Bright Data timed out: {error}") from error
        except httpx.RequestError as error:
            logger.error(f"Network error while triggering collector {effective_collector}: {error}")
            raise BrightDataError(f"Failed to connect to Bright Data API: {error}") from error

        if response.status_code in (401, 403):
            logger.error(f"Authentication failed for Bright Data: {response.status_code}")
            raise BrightDataAuthError(
                f"Bright Data authentication failed ({response.status_code}). Check your API key."
            )
        elif response.status_code != 200:
            logger.error(f"Bright Data trigger failed with HTTP {response.status_code}: {response.text}")
            raise BrightDataJobError(
                f"Bright Data trigger error ({response.status_code}): {response.text}"
            )

        try:
            data = response.json()
        except Exception:
            # Some DCA endpoints return raw job ID string
            raw_text = response.text.strip().strip('"')
            if raw_text:
                logger.info(f"Job triggered successfully. Job ID: {raw_text}")
                return raw_text
            raise BrightDataJobError("Empty or malformed trigger response from Bright Data.")

        job_id = None
        if isinstance(data, dict):
            job_id = data.get("collection_id") or data.get("response_id") or data.get("job_id")
        elif isinstance(data, str):
            job_id = data

        if not job_id:
            raise BrightDataJobError(f"Bright Data response did not contain a valid job ID: {data}")

        logger.info(f"Job triggered successfully. Job ID: {job_id}")
        return str(job_id)

    async def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Poll dataset endpoint to inspect the current execution status."""
        api_key, _ = self._ensure_configured()
        endpoint = f"{self._base_url}/dataset"
        params = {"id": job_id}

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.get(
                    endpoint,
                    params=params,
                    headers=self._get_headers(api_key),
                )
        except httpx.TimeoutException as error:
            raise BrightDataTimeoutError(f"Status check timed out for job {job_id}: {error}") from error
        except httpx.RequestError as error:
            raise BrightDataError(f"Network error checking status for job {job_id}: {error}") from error

        if response.status_code in (401, 403):
            raise BrightDataAuthError(f"Bright Data auth failure during status check ({response.status_code}).")
        elif response.status_code not in (200, 202):
            raise BrightDataJobError(f"Status check failed ({response.status_code}): {response.text}")

        # If status_code is 200, parse dataset results (supports JSON, JSONL, array, or single dict)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "").lower()
            raw_text = response.text.strip()

            # Check if JSONL / newline-delimited JSON
            if "\n" in raw_text or "jsonl" in content_type or "ndjson" in content_type:
                records = self._parse_jsonl_records(raw_text)
                if records:
                    return {"status": "completed", "data": records, "count": len(records)}

            try:
                data = response.json()
            except Exception as error:
                raise BrightDataJobError(f"Malformed response when checking status for job {job_id}: {response.text}") from error

            return self._parse_status_payload(data)

        # For HTTP 202 (Accepted / Still collecting)
        try:
            data = response.json()
            if isinstance(data, dict) and str(data.get("status", "")).lower() in _FAILURE_STATUSES:
                return {"status": "failed", "error": data.get("error") or data.get("message")}
        except Exception:
            pass

        return {"status": "running", "message": "Job in progress"}

    @staticmethod
    def _parse_jsonl_records(raw_text: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for line in raw_text.splitlines():
            line_str = line.strip()
            if line_str:
                try:
                    records.append(json.loads(line_str))
                except Exception:
                    pass
        return records

    @staticmethod
    def _parse_status_payload(data: Any) -> dict[str, Any]:
        if isinstance(data, list):
            return {"status": "completed", "data": data, "count": len(data)}

        if isinstance(data, dict):
            status_str = str(data.get("status", "")).lower()
            if status_str in _TERMINAL_COMPLETED_STATUSES:
                res_data = data.get("records") or data.get("data") or [data]
                return {"status": "completed", "data": res_data, "count": len(res_data)}
            elif status_str in _IN_PROGRESS_STATUSES:
                return {"status": "running", "message": data.get("message", "Job in progress")}
            elif status_str in _FAILURE_STATUSES:
                error_msg = data.get("error") or data.get("message") or "Unknown remote error"
                return {"status": "failed", "error": error_msg}
            else:
                # Single scraped record dict (e.g. {"url": "...", "title": "..."})
                return {"status": "completed", "data": [data], "count": 1}

        return {"status": "completed", "data": [data], "count": 1}

    async def fetch_results(self, job_id: str) -> list[dict[str, Any]]:
        """Fetch the completed records for a given job_id."""
        status_info = await self.get_job_status(job_id)
        status = status_info.get("status")

        if status == "failed":
            raise BrightDataJobError(f"Cannot fetch results: Job {job_id} failed: {status_info.get('error')}")
        elif status == "running":
            raise BrightDataJobError(f"Cannot fetch results: Job {job_id} is still in progress.")

        data = status_info.get("data")
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        return []

    async def scrape_and_collect(
        self,
        collector_id: Optional[str] = None,
        inputs: Optional[list[dict[str, Any]]] = None,
        poll_interval: float = 2.0,
        max_poll_seconds: float = 120.0,
    ) -> list[dict[str, Any]]:
        """Trigger collector, poll asynchronously until completion, and return results."""
        job_id = await self.trigger_scraper(collector_id=collector_id, inputs=inputs)
        logger.info(f"Polling job {job_id} every {poll_interval}s (max {max_poll_seconds}s)...")

        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_poll_seconds:
                logger.error(f"Polling exceeded maximum duration of {max_poll_seconds}s for job {job_id}")
                raise BrightDataTimeoutError(
                    f"Bright Data scraping timed out after {max_poll_seconds:.1f}s for job {job_id}."
                )

            status_info = await self.get_job_status(job_id)
            current_status = status_info.get("status")

            if current_status == "completed":
                results = status_info.get("data", [])
                logger.info(f"Job {job_id} completed successfully with {len(results)} record(s)")
                return results
            elif current_status == "failed":
                err = status_info.get("error", "Remote collection failure")
                logger.error(f"Job {job_id} failed on Bright Data: {err}")
                raise BrightDataJobError(f"Bright Data job {job_id} failed: {err}")

            logger.debug(f"Job {job_id} is still {current_status}. Waiting {poll_interval}s...")
            await asyncio.sleep(poll_interval)

    async def scrape_via_cli(
        self,
        collector_id: str,
        url: str,
        timeout_seconds: float = 120.0,
    ) -> list[dict[str, Any]]:
        """Execute scraper collector using Bright Data CLI as a reliable direct runner."""
        api_key = self.api_key or ""
        env = os.environ.copy()
        if api_key:
            env["BRIGHTDATA_API_KEY"] = api_key

        npx_bin = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
        cmd = [npx_bin, "-p", "@brightdata/cli", "brightdata", "scraper", "run", collector_id, url, "--json"]

        logger.info(f"Executing CLI scraper run: collector={collector_id} url={url}")

        try:
            if sys.platform == "win32":
                cmd_str = f'npx -p @brightdata/cli brightdata scraper run {collector_id} "{url}" --json'
                proc = await asyncio.create_subprocess_shell(
                    cmd_str,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                )
            else:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
        except asyncio.TimeoutError as error:
            logger.error(f"CLI scrape timed out after {timeout_seconds}s for {url}")
            raise BrightDataTimeoutError(f"CLI scrape timed out after {timeout_seconds}s: {url}") from error
        except Exception as error:
            logger.error(f"Failed to execute CLI scraper: {error}")
            raise BrightDataError(f"Failed to execute CLI scraper: {error}") from error

        out_text = stdout.decode("utf-8", errors="replace").strip()
        err_text = stderr.decode("utf-8", errors="replace").strip()

        if proc.returncode != 0:
            logger.error(f"CLI scraper failed with returncode {proc.returncode}: {err_text}")
            raise BrightDataJobError(f"CLI scraper failed ({proc.returncode}): {err_text or out_text}")

        # Parse JSON from stdout (may have status/polling logs preceding the json payload)
        return self._extract_json_from_text(out_text)

    @staticmethod
    def _extract_json_from_text(out_text: str) -> list[dict[str, Any]]:
        try:
            # Look for JSON array or object in output
            start_idx = out_text.find("[")
            end_idx = out_text.rfind("]")
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                json_str = out_text[start_idx : end_idx + 1]
                data = json.loads(json_str)
                if isinstance(data, list):
                    return data

            # Fallback to direct json.loads
            data = json.loads(out_text)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
        except Exception as error:
            logger.warning(f"Could not parse JSON from CLI output: {error}. Raw text: {out_text[:200]}")

        return []

