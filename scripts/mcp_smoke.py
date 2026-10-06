from __future__ import annotations

import asyncio
import os
import tempfile

os.environ["FINANCIAL_WRITING_DATA_DIR"] = tempfile.mkdtemp(prefix="financial-writing-mcp-")
os.environ["FINANCIAL_WRITING_REQUIRE_RENDER"] = "0"

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from financial_writing_agent.mcp_server import mcp


async def main() -> None:
    async with mcp.run_http_async(host="127.0.0.1", port=8765, streamable_http_path="/mcp", stateless_http=True, json_response=True):
        async with streamable_http_client("http://127.0.0.1:8765/mcp") as (read_stream, write_stream, _):
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
                    raise SystemExit(f"missing MCP tools: {missing}")
                result = await session.call_tool(
                    "start_writing_task",
                    arguments={"prompt": "smoke test only; do not research or draft"},
                )
                if result.isError:
                    raise SystemExit("start_writing_task failed")
                print(f"PASS: {len(names)} MCP tools exposed and start_writing_task callable")


if __name__ == "__main__":
    asyncio.run(main())
