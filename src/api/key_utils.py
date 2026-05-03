"""Helpers for API key storage and lookup."""

from __future__ import annotations

import hashlib


def hash_api_key(api_key: str) -> str:
    """Return the hex SHA-256 hash of a plaintext API key."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def key_prefix(api_key: str, visible_chars: int = 8) -> str:
    """Return a short display prefix for UI use."""
    return api_key[:visible_chars]
