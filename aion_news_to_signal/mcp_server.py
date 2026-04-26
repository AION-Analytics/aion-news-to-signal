#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Any

from aion import analyze
from mcp.server.fastmcp import FastMCP


server = FastMCP(
    name="AION News-to-Signal MCP Server",
    instructions=(
        "Use this server to analyze Indian financial headlines and return structured "
        "sector-level trading signals, including which sectors to long or short."
    ),
)


@server.tool(
    name="analyze_headline",
    description=(
        "Analyze one Indian financial headline and return sector-level trading signals, "
        "top positive and negative sectors, stakeholder views, and the resolved event."
    ),
)
def analyze_headline(headline: str, published_at: str | None = None) -> dict[str, Any]:
    return analyze(headline, published_at=published_at)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AION News-to-Signal MCP server.")
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
