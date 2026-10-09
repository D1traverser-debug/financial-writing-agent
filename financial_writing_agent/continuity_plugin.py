from __future__ import annotations

import os

from . import runtime_service as impl
from .continuity import continuity_metadata, list_resumable_states

# Patch the Runtime service before plugin_server registers the existing frozen
# 16-tool surface. This preserves tool names/count while making summaries and
# ordinary continuation discovery Continuity-v2-safe.
_original_summary = impl._summary


def _continuity_summary(state, *, detail: bool = False):
    raw = _original_summary(state, detail=detail)
    raw.update(continuity_metadata(state))
    return raw


def _safe_recent_tasks(limit: int = 10, include_complete: bool = False):
    states = list_resumable_states(impl.store, limit=limit, include_complete=include_complete)
    return [_continuity_summary(state) for state in states]


impl._summary = _continuity_summary
impl.list_recent_writing_tasks = _safe_recent_tasks

from . import plugin_server as base  # noqa: E402  (must register after patch)

mcp = base.mcp


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )


if __name__ == "__main__":
    main()
