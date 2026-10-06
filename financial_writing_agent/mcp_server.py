"""Compatibility entry point for the public Financial Writing MCP server.

The only tool/resource registration surface lives in ``plugin_server.py``.
Runtime business logic lives in ``runtime_service.py``. Keeping this thin shim
prevents older imports from breaking without maintaining a second MCP surface.
"""
from __future__ import annotations

from .plugin_server import main, mcp

__all__ = ["mcp", "main"]


if __name__ == "__main__":
    main()
