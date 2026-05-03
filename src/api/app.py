"""FastAPI gateway for AION India Event Intelligence with quota and rate enforcement."""

from __future__ import annotations

import hashlib
import logging
import time

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request

from aion import analyze as aion_analyze

from .quota_manager import consume_quota
from .rate_limiter import rate_limiter
from .usage_logger import log_to_clickhouse


logger = logging.getLogger(__name__)
app = FastAPI(title="AION India Event Intelligence API")


def _log_usage_analytics(
    api_key: str,
    endpoint: str,
    latency_ms: float,
    status: int,
    request_hash: str,
    ip_address: str,
) -> None:
    try:
        log_to_clickhouse(api_key, endpoint, latency_ms, status, request_hash, ip_address)
    except Exception:
        logger.exception("ClickHouse usage logging failed")


@app.post("/v1/analyze")
async def analyze_endpoint(request: Request, background_tasks: BackgroundTasks):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    body = await request.json()
    headline = body.get("headline")
    if not headline or not isinstance(headline, str):
        raise HTTPException(status_code=400, detail="Missing or invalid headline")

    if not rate_limiter.is_allowed(api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    quota = consume_quota(api_key)
    if not quota["allowed"]:
        reason = quota["reason"]
        if reason == "invalid_key":
            raise HTTPException(status_code=401, detail="Invalid API key")
        if reason == "key_disabled":
            raise HTTPException(status_code=403, detail="Key disabled")
        raise HTTPException(status_code=429, detail=f"Quota exceeded: {reason}")
    request.state.api_key_context = quota

    start = time.perf_counter()
    try:
        result = aion_analyze(headline)
        status = 200
    except Exception as exc:
        result = {"error": str(exc)}
        status = 500

    latency_ms = (time.perf_counter() - start) * 1000
    request_hash = hashlib.sha256(headline.encode()).hexdigest()[:16]
    ip_address = request.client.host if request.client else ""

    background_tasks.add_task(
        _log_usage_analytics,
        api_key,
        "/v1/analyze",
        latency_ms,
        status,
        request_hash,
        ip_address,
    )

    return result
