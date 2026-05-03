"""FastAPI API backend for AION key provisioning, billing, and inference."""

from __future__ import annotations

import hashlib
import os
import secrets
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg2
import razorpay
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from aion import analyze as aion_analyze

from .key_utils import hash_api_key
from .quota_manager import consume_quota, ensure_api_key_schema
from .rate_limiter import rate_limiter
from .usage_logger import log_to_clickhouse


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(title="AION API Backend")
IST = ZoneInfo("Asia/Kolkata")


RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")

PG_DSN = (
    f"dbname={os.getenv('AION_API_DB_NAME', 'aion_api')} "
    f"user={os.getenv('AION_API_DB_USER', 'aion_api')} "
    f"password={os.getenv('AION_API_DB_PASSWORD', '')} "
    f"host={os.getenv('AION_API_DB_HOST', 'localhost')} "
    f"port={os.getenv('AION_API_DB_PORT', '5432')}"
)

rz_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


class FreeSignupRequest(BaseModel):
    email: str


class PaidSignupRequest(BaseModel):
    email: str
    plan: str = "builder"


class AnalyzeRequest(BaseModel):
    headline: str


class TopupRequest(BaseModel):
    amount: float = 100.0


def generate_api_key() -> tuple[str, str, str]:
    plaintext = "aion_live_" + secrets.token_urlsafe(32)
    return plaintext, hash_api_key(plaintext), plaintext[:12]


def _next_reset_at() -> datetime:
    now = datetime.now(IST)
    year = now.year + (1 if now.month == 12 else 0)
    month = 1 if now.month == 12 else now.month + 1
    return datetime(year, month, 1, tzinfo=IST)


def db_execute(query: str, *args):
    conn = psycopg2.connect(PG_DSN)
    try:
        ensure_api_key_schema(conn)
        cur = conn.cursor()
        cur.execute(query, args)
        result = cur.fetchone() if cur.description else None
        conn.commit()
        cur.close()
        return result
    finally:
        conn.close()


def require_razorpay():
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=500, detail="Razorpay is not configured")


def _log_success_usage(
    api_key_plain: str,
    endpoint: str,
    latency_ms: float,
    status: int,
    request_hash: str,
    ip_address: str,
) -> None:
    log_to_clickhouse(api_key_plain, endpoint, latency_ms, status, request_hash, ip_address)


@app.post("/signup/free")
async def signup_free(data: FreeSignupRequest):
    email = data.email
    user = db_execute("SELECT id FROM users WHERE email = %s", email)
    user_id = user[0] if user else db_execute(
        "INSERT INTO users (email) VALUES (%s) RETURNING id",
        email,
    )[0]

    plaintext, key_hash, key_prefix = generate_api_key()
    db_execute(
        """
        INSERT INTO api_keys
            (user_id, key_hash, key_prefix, plan, monthly_limit, tier, monthly_quota, request_count, reset_at)
        VALUES (%s, %s, %s, 'free', 1000, 'free', 1000, 0, %s)
        """,
        user_id,
        key_hash,
        key_prefix,
        _next_reset_at(),
    )
    return {
        "api_key": plaintext,
        "plan": "free",
        "tier": "free",
        "monthly_limit": 1000,
        "monthly_quota": 1000,
        "warning": "Store this key securely. It will not be shown again.",
    }


@app.post("/signup/paid")
async def signup_paid(data: PaidSignupRequest):
    require_razorpay()

    email = data.email
    plan = data.plan
    limits = {"builder": 15000, "pro": 75000, "power": 250000}
    if plan not in limits:
        raise HTTPException(status_code=400, detail="Invalid plan")

    user_id = db_execute(
        """
        INSERT INTO users (email)
        VALUES (%s)
        ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
        RETURNING id
        """,
        email,
    )[0]

    subscription = rz_client.subscription.create(
        {
            "plan_id": f"plan_{plan}_monthly",
            "customer_notify": 1,
            "total_count": 60,
            "notes": {"email": email, "plan": plan},
        }
    )

    db_execute(
        """
        INSERT INTO pending_signups (user_id, plan, razorpay_subscription_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (razorpay_subscription_id)
        DO UPDATE SET plan = EXCLUDED.plan
        """,
        user_id,
        plan,
        subscription["id"],
    )

    return {"checkout_url": subscription.get("short_url", "")}


@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    if not RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Razorpay webhook secret is not configured")

    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    razorpay.Utility.verify_webhook_signature(
        body.decode(),
        signature,
        RAZORPAY_WEBHOOK_SECRET,
    )

    event = await request.json()

    if event["event"] in ("subscription.charged", "payment_link.paid"):
        payload = event["payload"]
        entity = payload.get("subscription", payload.get("payment_link", {}))
        ref_id = entity.get("entity", {}).get("id", entity.get("id"))

        if event["event"] == "subscription.charged":
            pending = db_execute(
                """
                SELECT user_id, plan
                FROM pending_signups
                WHERE razorpay_subscription_id = %s
                """,
                ref_id,
            )
            if pending:
                user_id, plan = pending
                plaintext, key_hash, key_prefix = generate_api_key()
                limits = {"builder": 15000, "pro": 75000, "power": 250000}
                db_execute(
                    """
                    INSERT INTO api_keys
                        (
                            user_id,
                            key_hash,
                            key_prefix,
                            plan,
                            monthly_limit,
                            tier,
                            monthly_quota,
                            request_count,
                            reset_at,
                            razorpay_subscription_id
                        )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s)
                    """,
                    user_id,
                    key_hash,
                    key_prefix,
                    plan,
                    limits[plan],
                    plan,
                    limits[plan],
                    _next_reset_at(),
                    ref_id,
                )
                db_execute(
                    "DELETE FROM pending_signups WHERE razorpay_subscription_id = %s",
                    ref_id,
                )
                return {
                    "status": "ok",
                    "provisioned": True,
                    "api_key": plaintext,
                    "warning": "Store this key securely. It will not be shown again.",
                }

        elif event["event"] == "payment_link.paid":
            notes = entity.get("notes", {})
            api_key_hash = notes.get("api_key_hash")
            credits = int(notes.get("credits", 0))
            if api_key_hash and credits:
                db_execute(
                    """
                    UPDATE api_keys
                    SET monthly_limit = monthly_limit + %s,
                        monthly_quota = COALESCE(monthly_quota, monthly_limit, 0) + %s
                    WHERE key_hash = %s
                    """,
                    credits,
                    credits,
                    api_key_hash,
                )

    return {"status": "ok"}


@app.post("/v1/analyze")
async def analyze_endpoint(
    data: AnalyzeRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    api_key_plain = request.headers.get("X-API-Key")
    if not api_key_plain:
        raise HTTPException(status_code=401, detail="Missing API key")

    if not rate_limiter.is_allowed(api_key_plain):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    quota = consume_quota(api_key_plain)
    if not quota["allowed"]:
        reason = quota["reason"]
        if reason == "invalid_key":
            raise HTTPException(status_code=401, detail="Invalid API key")
        if reason == "key_disabled":
            raise HTTPException(status_code=403, detail="Key disabled")
        limit = quota.get("limit", 0)
        raise HTTPException(status_code=429, detail=f"Monthly quota exceeded ({limit})")
    request.state.api_key_context = quota

    headline = data.headline
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
        _log_success_usage,
        api_key_plain,
        "/v1/analyze",
        latency_ms,
        status,
        request_hash,
        ip_address,
    )

    return JSONResponse(content=result, status_code=status)


@app.post("/account/topup")
async def topup(data: TopupRequest, request: Request):
    require_razorpay()

    api_key_plain = request.headers.get("X-API-Key")
    if not api_key_plain:
        raise HTTPException(status_code=401, detail="Missing API key")

    key_hash = hash_api_key(api_key_plain)
    row = db_execute("SELECT id, plan FROM api_keys WHERE key_hash = %s", key_hash)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid API key")

    amount = data.amount
    credits = int(amount / 0.10)

    payment_link = rz_client.payment_link.create(
        {
            "amount": int(amount * 100),
            "currency": "INR",
            "description": f"AION Top-Up: {credits} extra headlines",
            "notes": {"api_key_hash": key_hash, "credits": credits, "type": "topup"},
        }
    )

    return {"checkout_url": payment_link["short_url"], "credits_added": credits}
