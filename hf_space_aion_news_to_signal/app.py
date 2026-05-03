#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any

import gradio as gr
import requests


API_BASE_URL = os.getenv("AION_API_BASE_URL", "https://api.aiondashboard.site").rstrip("/")
SPACE_API_KEY = os.getenv("AION_SPACE_API_KEY", "").strip()
ACCESS_PAGE_URL = os.getenv(
    "AION_ACCESS_PAGE_URL",
    "https://dashboard.aiondashboard.site/models/news-to-signal",
)


def analyze_payload(headline: str, published_at: str | None = None) -> dict[str, Any]:
    headline = (headline or "").strip()
    if not headline:
        return {"error": "headline is required"}
    if not SPACE_API_KEY:
        return {
            "error": "demo_backend_not_configured",
            "detail": "This demo surface is not configured with its internal API key.",
            "access_url": ACCESS_PAGE_URL,
        }

    payload: dict[str, Any] = {"headline": headline}
    if published_at:
        payload["published_at"] = published_at

    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/analyze",
            headers={"X-API-Key": SPACE_API_KEY},
            json=payload,
            timeout=45,
        )
        if response.status_code >= 400:
            detail: Any
            try:
                detail = response.json()
            except Exception:
                detail = response.text[:400]
            return {
                "error": "api_request_failed",
                "status": response.status_code,
                "detail": detail,
                "access_url": ACCESS_PAGE_URL,
            }
        return response.json()
    except requests.RequestException as exc:
        return {
            "error": "demo_unavailable",
            "detail": str(exc),
            "access_url": ACCESS_PAGE_URL,
        }


with gr.Blocks(title="AION India Event Intelligence") as demo:
    gr.Markdown(
        f"""
        # AION India Event Intelligence

        Formerly `aion-news-to-signal`.

        This is a demo UI backed by the managed AION API.

        Production access requires your own API key:
        - `{ACCESS_PAGE_URL}`

        Production API contract:
        - `POST {API_BASE_URL}/v1/analyze`
        - header: `X-API-Key: <key>`

        This Space is not the supported production runtime.
        """
    )
    with gr.Row():
        headline = gr.Textbox(
            label="Headline",
            lines=2,
            placeholder="RBI hikes repo rate by 25 bps",
        )
    with gr.Row():
        published_at = gr.Textbox(
            label="Published At (optional)",
            placeholder="2026-04-26",
        )
    run = gr.Button("Analyze", variant="primary")
    output = gr.JSON(label="Structured Output")

    examples = [
        ["RBI hikes repo rate by 25 bps", ""],
        ["Heatwave in Punjab during March damages wheat crop and threatens food inflation", ""],
        ["Unseasonal rainfall and hailstorm hit apple orchards in Himachal Pradesh in April", ""],
        ["Crude oil prices fall sharply", ""],
    ]
    gr.Examples(examples=examples, inputs=[headline, published_at])

    run.click(
        fn=analyze_payload,
        inputs=[headline, published_at],
        outputs=output,
        api_name="analyze",
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        show_error=True,
    )
