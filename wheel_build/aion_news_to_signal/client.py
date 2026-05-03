from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


DEFAULT_BASE_URL = (
    os.getenv("AION_API_BASE_URL")
    or os.getenv("AION_BASE_URL")
    or "https://api.aiondashboard.site"
).rstrip("/")


class AIONError(RuntimeError):
    """Raised when the managed AION API returns an invalid response."""


@dataclass
class AIONClient:
    api_key: str | None = None
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 30.0
    session: requests.Session | None = None

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self.session = self.session or requests.Session()
        self.api_key = self.api_key or os.getenv("AION_API_KEY", "").strip()

    def analyze(self, headline: str, published_at: str | None = None) -> dict[str, Any]:
        headline = (headline or "").strip()
        if not headline:
            raise AIONError("headline is required")
        if not self.api_key:
            raise AIONError(
                "AION_API_KEY is required. Set it in your environment or pass api_key to AIONClient."
            )

        payload: dict[str, Any] = {"headline": headline}
        if published_at:
            payload["published_at"] = published_at

        response = self.session.post(
            self.base_url + "/v1/analyze",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            },
            json=payload,
            timeout=self.timeout,
        )

        try:
            data = response.json()
        except Exception as exc:
            raise AIONError(f"invalid API response: {response.text[:300]}") from exc

        if response.status_code >= 400:
            detail = data.get("detail") if isinstance(data, dict) else data
            raise AIONError(f"API request failed ({response.status_code}): {detail}")

        if not isinstance(data, dict):
            raise AIONError(f"unexpected payload type: {type(data).__name__}")

        return data


def analyze(
    headline: str,
    published_at: str | None = None,
    *,
    api_key: str | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Analyze a headline using the managed AION India Event Intelligence API."""
    return AIONClient(api_key=api_key, base_url=base_url, timeout=timeout).analyze(
        headline=headline,
        published_at=published_at,
    )
