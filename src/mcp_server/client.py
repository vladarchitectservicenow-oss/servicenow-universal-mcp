"""ServiceNow REST API client."""

from base64 import b64encode
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import SNConfig


class ServiceNowClient:
    """Low-level REST client для ServiceNow."""

    def __init__(self, config: SNConfig):
        self.config = config
        self._auth_header = self._build_auth()
        self._base = config.url.rstrip("/")

    def _build_auth(self) -> str:
        raw = f"{self.config.username}:{self.config.password}"
        encoded = b64encode(raw.encode()).decode()
        return f"Basic {encoded}"

    def _headers(self, extra: dict | None = None) -> dict:
        h = {
            "Authorization": self._auth_header,
            "Accept": "application/json",
        }
        if extra:
            h.update(extra)
        return h

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self._base}{path}"
        timeout = kwargs.pop("timeout", self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.request(method, url, headers=self._headers(), **kwargs)
            resp.raise_for_status()
            return resp.json()

    # ── Count ─────────────────────────────────────────────────────────────
    async def count(self, table: str, query: str = "") -> int:
        """Count records via /api/now/stats/{table}."""
        params = {"sysparm_count": "true"}
        if query:
            params["sysparm_query"] = query
        data = await self._request("GET", f"/api/now/stats/{table}", params=params)
        return int(data["result"]["stats"]["count"])

    # ── List ──────────────────────────────────────────────────────────────
    async def list(
        self,
        table: str,
        fields: list[str] | None = None,
        query: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List records via /api/now/table/{table}."""
        params: dict[str, Any] = {"sysparm_limit": limit, "sysparm_offset": offset}
        if fields:
            params["sysparm_fields"] = ",".join(fields)
        if query:
            params["sysparm_query"] = query
        data = await self._request("GET", f"/api/now/table/{table}", params=params)
        return data.get("result", [])

    # ── Get ───────────────────────────────────────────────────────────────
    async def get(self, table: str, sys_id: str) -> dict:
        """Get single record."""
        data = await self._request("GET", f"/api/now/table/{table}/{sys_id}")
        return data.get("result", {})

    # ── Create ────────────────────────────────────────────────────────────
    async def create(self, table: str, payload: dict) -> dict:
        """Create record."""
        data = await self._request(
            "POST",
            f"/api/now/table/{table}",
            json=payload,
            headers=self._headers({"Content-Type": "application/json"}),
        )
        return data.get("result", {})

    # ── Update ────────────────────────────────────────────────────────────
    async def update(self, table: str, sys_id: str, payload: dict) -> dict:
        """Update record."""
        data = await self._request(
            "PUT",
            f"/api/now/table/{table}/{sys_id}",
            json=payload,
            headers=self._headers({"Content-Type": "application/json"}),
        )
        return data.get("result", {})

    # ── Delete ────────────────────────────────────────────────────────────
    async def delete(self, table: str, sys_id: str) -> bool:
        """Delete record. Returns True if successful."""
        await self._request("DELETE", f"/api/now/table/{table}/{sys_id}")
        return True
