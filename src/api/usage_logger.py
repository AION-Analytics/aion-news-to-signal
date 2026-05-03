"""Usage analytics logging for API requests."""

from __future__ import annotations

import os
from pathlib import Path

from clickhouse_driver import Client
from dotenv import load_dotenv
from .key_utils import hash_api_key


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _clickhouse_client() -> Client:
    return Client(
        host=os.getenv("AION_API_CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("AION_API_CLICKHOUSE_PORT", "9000")),
        database=os.getenv("AION_API_CLICKHOUSE_DB", "aion_api"),
        user=os.getenv("AION_API_CLICKHOUSE_USER", "default"),
        password=os.getenv("AION_API_CLICKHOUSE_PASSWORD", ""),
    )


def log_to_clickhouse(
    api_key: str,
    endpoint: str,
    latency_ms: float,
    status: int,
    request_hash: str,
    ip_address: str = "",
) -> None:
    """Synchronous insert intended for async fire-and-forget dispatch by caller."""
    client = _clickhouse_client()
    api_key_hash = hash_api_key(api_key)
    client.execute(
        """
        INSERT INTO api_usage_logs
            (api_key, endpoint, latency_ms, status, request_hash, ip_address)
        VALUES
        """,
        [
            (
                api_key_hash,
                endpoint,
                latency_ms,
                status,
                request_hash,
                ip_address,
            )
        ],
    )
