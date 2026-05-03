"""Postgres-backed API key validation and atomic quota consumption."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg2
from dotenv import load_dotenv

from .key_utils import hash_api_key


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

IST = ZoneInfo("Asia/Kolkata")
_SCHEMA_READY = False


def _connect():
    return psycopg2.connect(
        dbname=os.getenv("AION_API_DB_NAME", "aion_api"),
        user=os.getenv("AION_API_DB_USER", "aion_api"),
        password=os.getenv("AION_API_DB_PASSWORD"),
        host=os.getenv("AION_API_DB_HOST", "localhost"),
        port=os.getenv("AION_API_DB_PORT", "5432"),
    )


def _now_ist() -> datetime:
    return datetime.now(IST)


def _next_reset_at(now_ist: datetime | None = None) -> datetime:
    now_ist = now_ist or _now_ist()
    year = now_ist.year + (1 if now_ist.month == 12 else 0)
    month = 1 if now_ist.month == 12 else now_ist.month + 1
    return datetime(year, month, 1, tzinfo=IST)


def _ensure_api_keys_contract(conn) -> None:
    global _SCHEMA_READY
    if _SCHEMA_READY:
        return

    next_reset_at = _next_reset_at()
    current_cycle_start = _now_ist().date().replace(day=1)
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS tier TEXT")
        cur.execute("ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS monthly_quota INTEGER")
        cur.execute("ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS request_count INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS reset_at TIMESTAMPTZ")
        cur.execute("ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS last_used_at TIMESTAMPTZ")

        cur.execute("UPDATE api_keys SET tier = COALESCE(tier, plan) WHERE tier IS NULL")
        cur.execute(
            "UPDATE api_keys SET monthly_quota = COALESCE(monthly_quota, monthly_limit, 0) "
            "WHERE monthly_quota IS NULL"
        )
        cur.execute("UPDATE api_keys SET request_count = COALESCE(request_count, 0) WHERE request_count IS NULL")
        cur.execute("UPDATE api_keys SET reset_at = COALESCE(reset_at, %s) WHERE reset_at IS NULL", (next_reset_at,))

        cur.execute("SELECT to_regclass('public.usage_counters')")
        if cur.fetchone()[0]:
            cur.execute(
                """
                UPDATE api_keys ak
                SET request_count = GREATEST(COALESCE(ak.request_count, 0), uc.request_count)
                FROM usage_counters uc
                WHERE uc.api_key_id = ak.id
                  AND uc.month = %s
                """,
                (current_cycle_start,),
            )

    conn.commit()
    _SCHEMA_READY = True


def ensure_api_key_schema(conn=None) -> None:
    """Ensure the api_keys quota contract columns exist before reads or inserts."""
    if conn is not None:
        _ensure_api_keys_contract(conn)
        return
    with _connect() as owned_conn:
        _ensure_api_keys_contract(owned_conn)


def _fetch_key_context(cur, api_key_hash: str, default_reset_at: datetime):
    cur.execute(
        """
        SELECT
            id AS key_id,
            user_id,
            COALESCE(tier, plan) AS tier,
            COALESCE(monthly_quota, monthly_limit, 0) AS monthly_quota,
            COALESCE(request_count, 0) AS request_count,
            COALESCE(reset_at, %s) AS reset_at,
            is_active
        FROM api_keys
        WHERE key_hash = %s
        """,
        (default_reset_at, api_key_hash),
    )
    return cur.fetchone()


def check_quota(api_key: str) -> dict:
    """Read current quota state without consuming it."""
    now_ist = _now_ist()
    next_reset_at = _next_reset_at(now_ist)
    with _connect() as conn:
        _ensure_api_keys_contract(conn)
        with conn.cursor() as cur:
            row = _fetch_key_context(cur, hash_api_key(api_key), next_reset_at)
            if not row:
                return {"allowed": False, "reason": "invalid_key"}

            key_id, user_id, tier, monthly_quota, request_count, reset_at, is_active = row
            if not is_active:
                return {
                    "allowed": False,
                    "reason": "key_disabled",
                    "key_id": key_id,
                    "user_id": user_id,
                    "tier": tier,
                    "plan": tier,
                    "limit": monthly_quota,
                    "monthly_quota": monthly_quota,
                    "request_count": request_count,
                    "reset_at": reset_at,
                    "remaining": 0,
                }

            current_usage = 0 if reset_at <= now_ist else int(request_count)
            remaining = max(monthly_quota - current_usage, 0)
            allowed = remaining > 0

            return {
                "allowed": allowed,
                "reason": None if allowed else "quota_exceeded",
                "key_id": key_id,
                "user_id": user_id,
                "tier": tier,
                "plan": tier,
                "limit": monthly_quota,
                "monthly_quota": monthly_quota,
                "request_count": current_usage,
                "reset_at": reset_at,
                "remaining": remaining,
            }


def consume_quota(api_key: str) -> dict:
    """Atomically validate and consume one unit of monthly quota on api_keys."""
    now_ist = _now_ist()
    next_reset_at = _next_reset_at(now_ist)
    api_key_hash = hash_api_key(api_key)

    with _connect() as conn:
        _ensure_api_keys_contract(conn)
        with conn.cursor() as cur:
            row = _fetch_key_context(cur, api_key_hash, next_reset_at)
            if not row:
                return {"allowed": False, "reason": "invalid_key"}

            key_id, user_id, tier, monthly_quota, request_count, reset_at, is_active = row
            if not is_active:
                return {
                    "allowed": False,
                    "reason": "key_disabled",
                    "key_id": key_id,
                    "user_id": user_id,
                    "tier": tier,
                    "plan": tier,
                    "limit": monthly_quota,
                    "monthly_quota": monthly_quota,
                    "request_count": 0 if reset_at <= now_ist else int(request_count),
                    "reset_at": reset_at,
                    "remaining": 0,
                }

            if monthly_quota <= 0:
                return {
                    "allowed": False,
                    "reason": "quota_exceeded",
                    "key_id": key_id,
                    "user_id": user_id,
                    "tier": tier,
                    "plan": tier,
                    "limit": monthly_quota,
                    "monthly_quota": monthly_quota,
                    "request_count": 0 if reset_at <= now_ist else int(request_count),
                    "reset_at": reset_at,
                    "remaining": 0,
                }

            cur.execute(
                """
                UPDATE api_keys
                SET request_count = CASE
                        WHEN COALESCE(reset_at, %s) <= %s THEN 1
                        ELSE COALESCE(request_count, 0) + 1
                    END,
                    reset_at = CASE
                        WHEN COALESCE(reset_at, %s) <= %s THEN %s
                        ELSE COALESCE(reset_at, %s)
                    END,
                    tier = COALESCE(tier, plan),
                    monthly_quota = COALESCE(monthly_quota, monthly_limit, 0),
                    last_used_at = %s
                WHERE id = %s
                  AND is_active = TRUE
                  AND (
                    CASE
                        WHEN COALESCE(reset_at, %s) <= %s THEN 0
                        ELSE COALESCE(request_count, 0)
                    END
                  ) < COALESCE(monthly_quota, monthly_limit, 0)
                RETURNING
                    request_count,
                    reset_at,
                    COALESCE(tier, plan) AS tier,
                    COALESCE(monthly_quota, monthly_limit, 0) AS monthly_quota
                """,
                (
                    next_reset_at,
                    now_ist,
                    next_reset_at,
                    now_ist,
                    next_reset_at,
                    next_reset_at,
                    now_ist,
                    key_id,
                    next_reset_at,
                    now_ist,
                ),
            )
            updated = cur.fetchone()
            if not updated:
                cur.execute("SELECT is_active FROM api_keys WHERE id = %s", (key_id,))
                state = cur.fetchone()
                reason = "key_disabled" if state and not state[0] else "quota_exceeded"
                current_usage = 0 if reset_at <= now_ist else int(request_count)
                return {
                    "allowed": False,
                    "reason": reason,
                    "key_id": key_id,
                    "user_id": user_id,
                    "tier": tier,
                    "plan": tier,
                    "limit": monthly_quota,
                    "monthly_quota": monthly_quota,
                    "request_count": current_usage,
                    "reset_at": reset_at,
                    "remaining": max(monthly_quota - current_usage, 0),
                }

            current_usage, new_reset_at, resolved_tier, resolved_quota = updated

    current_usage = int(current_usage)
    resolved_quota = int(resolved_quota)
    return {
        "allowed": True,
        "reason": None,
        "key_id": key_id,
        "user_id": user_id,
        "tier": resolved_tier,
        "plan": resolved_tier,
        "limit": resolved_quota,
        "monthly_quota": resolved_quota,
        "request_count": current_usage,
        "reset_at": new_reset_at,
        "remaining": max(resolved_quota - current_usage, 0),
    }
