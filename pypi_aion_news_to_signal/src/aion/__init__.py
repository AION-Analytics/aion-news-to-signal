from __future__ import annotations

from aion_news_to_signal import AIONClient, AIONError, analyze


def get_pipeline(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> AIONClient:
    """Compatibility shim for legacy imports.

    The distributable package is API-first. This helper keeps older
    `from aion import get_pipeline` flows working by returning the managed
    AION API client instead of a local runtime.
    """

    kwargs: dict[str, object] = {"api_key": api_key, "timeout": timeout}
    if base_url:
        kwargs["base_url"] = base_url
    return AIONClient(**kwargs)


__all__ = ["AIONClient", "AIONError", "analyze", "get_pipeline"]
