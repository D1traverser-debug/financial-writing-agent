from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import tempfile
import time

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

PORT = 8765
URL = f"http://127.0.0.1:{PORT}/mcp"


def wait_for_port(host: str, port: int, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError(f"MCP server did not open {host}:{port} within {timeout}s")


async def verify() -> None:
    async with streamable_http_client(URL) as streams:
        read_stream, write_stream = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            required = {
                "start_writing_task",
                "get_writing_task",
                "list_recent_writing_tasks",
                "submit_research",
                "submit_research_audit",
                "submit_editorial_plan",
                "submit_headlines",
                "submit_draft",
                "submit_editorial_audit",
                "build_and_mechanically_audit_delivery",
                "submit_final_audit",
            }
            missing = sorted(required - names)
            if missing:
                raise RuntimeError(f"missing MCP tools: {missing}")
            result = await session.call_tool(
                "start_writing_task",
                arguments={"prompt": "smoke test only; do not research or draft"},
            )
            if result.is_error:
                raise RuntimeError(f"start_writing_task failed: {result.content}")
            print(f"PASS: {len(names)} MCP tools exposed and start_writing_task callable")


def main() -> None:
    env = os.environ.copy()
    env["FINANCIAL_WRITING_DATA_DIR"] = tempfile.mkdtemp(prefix="financial-writing-mcp-")
    env["FINANCIAL_WRITING_REQUIRE_RENDER"] = "0"
    env["MCP_HOST"] = "127.0.0.1"
    env["MCP_PORT"] = str(PORT)
    proc = subprocess.Popen(
        [sys.executable, "-m", "financial_writing_agent.mcp_server"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_port("127.0.0.1", PORT)
        asyncio.run(verify())
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        if proc.returncode not in {0, -15} and proc.stdout:
            print(proc.stdout.read())


if __name__ == "__main__":
    main()
