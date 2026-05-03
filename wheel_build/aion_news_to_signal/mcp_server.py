#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Any

from aion_news_to_signal import analyze
from mcp.server.fastmcp import FastMCP


server = FastMCP(
    name="AION India Event Intelligence MCP Server",
    instructions=(
        "Use this server to call AION India Event Intelligence via API and return "
        "structured sector intelligence for Indian financial news. "
        "An API key is required through the AION_API_KEY environment variable. "
        "This system is quota-controlled and does not execute trades or generate executable orders."
    ),
)


@server.tool(
    name="analyze_news",
    description=(
        "Analyze one Indian financial headline via the managed AION API and return only the sector_vector. "
        "Requires API key configuration and returns structured sector intelligence, not trading signals."
    ),
)
def analyze_news(headline: str, published_at: str | None = None) -> dict[str, Any]:
    result = analyze(headline, published_at=published_at)
    return {"sector_vector": result.get("sector_vector", {})}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AION India Event Intelligence MCP server.")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="MCP transport to run. Default: stdio",
    )
    args = parser.parse_args()
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
