"""Compatibility entry point for the public Financial Writing MCP server.

The registered tool/resource surface still lives in ``plugin_server.py``.
``continuity_plugin.py`` wraps that same 16-tool surface with Continuity v2
summary metadata and safe ordinary task discovery. This shim routes legacy
entrypoints through the wrapper without maintaining a second MCP surface.
"""
from __future__ import annotations

from .continuity_plugin import main, mcp

__all__ = ["mcp", "main"]


if __name__ == "__main__":
    main()
