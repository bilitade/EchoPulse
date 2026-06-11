"""EchoPulse MCP server — PostgreSQL feedback tools for n8n."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

MCP_DIR = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("mcp_tools", MCP_DIR / "mcp_tools.py")
mcp_tools = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mcp_tools)

_mcp_dir = str(MCP_DIR)
while _mcp_dir in sys.path:
    sys.path.remove(_mcp_dir)
for module_name in list(sys.modules):
    if module_name == "mcp" or module_name.startswith("mcp."):
        del sys.modules[module_name]

from fastmcp import FastMCP

mcp = FastMCP(
    "EchoPulse",
    instructions=(
        "Analyze categorized customer feedback stored in PostgreSQL. "
        "Call get_summary_stats for overviews, then search_feedback or get_top_issues as needed."
    ),
)


@mcp.tool()
def get_summary_stats(days: int = 7) -> dict:
    """Return feedback volume and breakdowns by category, severity, and sentiment."""
    return mcp_tools.get_summary_stats(days=days)


@mcp.tool()
def search_feedback(query: str, limit: int = 10) -> dict:
    """Full-text search over review text and summaries."""
    return mcp_tools.search_feedback(query=query, limit=limit)


@mcp.tool()
def get_top_issues(category: str | None = None, days: int = 7, limit: int = 5) -> dict:
    """Return the most frequent issues, optionally filtered by category."""
    return mcp_tools.get_top_issues(category=category, days=days, limit=limit)


@mcp.tool()
def get_trend(
    category: str | None = None,
    severity: str | None = None,
    days: int = 7,
) -> dict:
    """Return daily feedback counts over a time window."""
    return mcp_tools.get_trend(category=category, severity=severity, days=days)


@mcp.tool()
def get_critical_items(resolved: bool = False, limit: int = 10) -> dict:
    """Return high- and critical-severity feedback items."""
    return mcp_tools.get_critical_items(resolved=resolved, limit=limit)


@mcp.tool()
def mark_resolved(feedback_id: int, reason: str = "") -> dict:
    """Mark a feedback record as resolved."""
    return mcp_tools.mark_resolved(feedback_id=feedback_id, reason=reason)


if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", "8000"))
    host = os.getenv("MCP_HOST", "0.0.0.0")
    transport = os.getenv("MCP_TRANSPORT", "sse")
    mcp.run(transport=transport, host=host, port=port)
