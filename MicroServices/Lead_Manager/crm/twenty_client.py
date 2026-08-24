"""
Twenty CRM REST API Client.
Provides async integration with open-source Twenty CRM (https://github.com/twentyhq/twenty).
"""

import logging
from typing import Any

import httpx
import sniffio

logger = logging.getLogger("TwentyCRMClient")


class TwentyCRMClient:
    """
    Asynchronous client for interacting with self-hosted or cloud Twenty CRM instance.
    Standard REST Endpoints:
      - /rest/companies
      - /rest/people
      - /rest/opportunities
      - /rest/notes
      - /rest/tasks
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        api_key: str | None = None,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _client(self) -> httpx.AsyncClient:
        sniffio.current_async_library_cvar.set("asyncio")
        return httpx.AsyncClient(timeout=self.timeout)

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def is_healthy(self) -> bool:
        """Check if Twenty CRM instance is reachable."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(
                    f"{self.base_url}/healthz", headers=self._get_headers()
                )
                if res.status_code == 200:
                    return True
                # Check root or rest endpoint as fallback
                res_root = await client.get(
                    f"{self.base_url}/rest/companies", headers=self._get_headers()
                )
                return res_root.status_code in (200, 401, 403)
        except Exception:
            return False

    async def create_company(
        self,
        name: str,
        domain_name: str | None = None,
        address: str | None = None,
        industry: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Creates a Company record in Twenty CRM."""
        payload: dict[str, Any] = {"name": name}
        if domain_name:
            payload["domainName"] = (
                domain_name.replace("https://", "").replace("http://", "").rstrip("/")
            )
        if address:
            payload["address"] = {"addressStreet1": address}
        if industry:
            payload["industry"] = industry

        url = f"{self.base_url}/rest/companies"
        try:
            async with self._client() as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code in (200, 201):
                    data = res.json()
                    logger.info(f"Twenty CRM: Created company '{name}'")
                    return data.get("data", data)
                else:
                    logger.warning(
                        f"Twenty CRM create_company returned HTTP {res.status_code}: {res.text}"
                    )
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": res.text,
                    }
        except Exception as e:
            logger.warning(f"Twenty CRM create_company connection error: {e}")
            return {"success": False, "error": str(e)}

    async def create_person(
        self,
        first_name: str,
        last_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company_id: str | None = None,
    ) -> dict[str, Any]:
        """Creates a Person (Contact) record in Twenty CRM."""
        payload: dict[str, Any] = {
            "name": {
                "firstName": first_name,
                "lastName": last_name or "",
            }
        }
        if email:
            payload["emails"] = {"primaryEmail": email}
        if phone:
            payload["phones"] = {"primaryPhone": phone}
        if company_id:
            payload["companyId"] = company_id

        url = f"{self.base_url}/rest/people"
        try:
            async with self._client() as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code in (200, 201):
                    data = res.json()
                    logger.info(
                        f"Twenty CRM: Created contact '{first_name} {last_name or ''}'"
                    )
                    return data.get("data", data)
                else:
                    logger.warning(
                        f"Twenty CRM create_person returned HTTP {res.status_code}: {res.text}"
                    )
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": res.text,
                    }
        except Exception as e:
            logger.warning(f"Twenty CRM create_person connection error: {e}")
            return {"success": False, "error": str(e)}

    async def create_opportunity(
        self,
        name: str,
        company_id: str | None = None,
        amount_usd: float = 0.0,
        stage: str = "PROSPECT",
        point_of_contact_id: str | None = None,
    ) -> dict[str, Any]:
        """Creates an Opportunity record in Twenty CRM."""
        payload: dict[str, Any] = {
            "name": name,
            "stage": stage,
        }
        if company_id:
            payload["companyId"] = company_id
        if point_of_contact_id:
            payload["pointOfContactId"] = point_of_contact_id
        if amount_usd > 0:
            payload["amount"] = {
                "amountMicros": int(amount_usd * 1_000_000),
                "currencyCode": "USD",
            }

        url = f"{self.base_url}/rest/opportunities"
        try:
            async with self._client() as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code in (200, 201):
                    data = res.json()
                    logger.info(f"Twenty CRM: Created opportunity '{name}'")
                    return data.get("data", data)
                else:
                    logger.warning(
                        f"Twenty CRM create_opportunity returned HTTP {res.status_code}: {res.text}"
                    )
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": res.text,
                    }
        except Exception as e:
            logger.warning(f"Twenty CRM create_opportunity connection error: {e}")
            return {"success": False, "error": str(e)}

    async def create_note(
        self,
        title: str,
        body: str,
        targetable_id: str | None = None,
        targetable_type: str = "company",
    ) -> dict[str, Any]:
        """Creates a Note / Activity record in Twenty CRM (useful for call transcripts)."""
        payload: dict[str, Any] = {
            "title": title,
            "body": body,
        }
        if targetable_id:
            payload["targetableId"] = targetable_id
            payload["targetableType"] = targetable_type

        url = f"{self.base_url}/rest/notes"
        try:
            async with self._client() as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code in (200, 201):
                    data = res.json()
                    logger.info(f"Twenty CRM: Created note '{title}'")
                    return data.get("data", data)
                else:
                    logger.warning(
                        f"Twenty CRM create_note returned HTTP {res.status_code}: {res.text}"
                    )
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": res.text,
                    }
        except Exception as e:
            logger.warning(f"Twenty CRM create_note connection error: {e}")
            return {"success": False, "error": str(e)}

    async def create_task(
        self,
        title: str,
        body: str | None = None,
        due_at_iso: str | None = None,
        status: str = "TODO",
        targetable_id: str | None = None,
        targetable_type: str = "company",
    ) -> dict[str, Any]:
        """Creates an actionable Task in Twenty CRM."""
        payload: dict[str, Any] = {
            "title": title,
            "status": status,
        }
        if body:
            payload["body"] = body
        if due_at_iso:
            payload["dueAt"] = due_at_iso
        if targetable_id:
            payload["targetableId"] = targetable_id
            payload["targetableType"] = targetable_type

        url = f"{self.base_url}/rest/tasks"
        try:
            async with self._client() as client:
                res = await client.post(url, json=payload, headers=self._get_headers())
                if res.status_code in (200, 201):
                    data = res.json()
                    logger.info(f"Twenty CRM: Created task '{title}'")
                    return data.get("data", data)
                else:
                    logger.warning(
                        f"Twenty CRM create_task returned HTTP {res.status_code}: {res.text}"
                    )
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": res.text,
                    }
        except Exception as e:
            logger.warning(f"Twenty CRM create_task connection error: {e}")
            return {"success": False, "error": str(e)}
