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

REQUIRED = {
    "start_writing_task",
    "get_writing_task",
    "list_recent_writing_tasks",
    "record_knowledge_context",
    "submit_research",
    "submit_research_audit",
    "submit_editorial_plan",
    "submit_headlines",
    "submit_draft",
    "submit_style_audit",
    "submit_editorial_audit",
    "submit_visual_package",
    "build_and_mechanically_audit_delivery",
    "record_knowledge_writeback",
    "submit_final_audit",
}

READ_ONLY = {"get_writing_task", "list_recent_writing_tasks"}


def wait_for_port(host: str, port: int, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError(f"MCP server did not open {host}:{port} within {timeout}s")


def validate_descriptor(tool) -> None:
    descriptor = tool.model_dump(by_alias=True, exclude_none=True)
    annotations = descriptor.get("annotations") or {}
    for key in ("readOnlyHint", "openWorldHint", "destructiveHint"):
        if key not in annotations or not isinstance(annotations[key], bool):
            raise RuntimeError(f"{tool.name} missing explicit annotation {key}: {annotations}")
    if annotations["readOnlyHint"] != (tool.name in READ_ONLY):
        raise RuntimeError(f"{tool.name} has incorrect readOnlyHint")
    if annotations["destructiveHint"] is not False:
        raise RuntimeError(f"{tool.name} unexpectedly marked destructive")
    expected_open_world = tool.name == "submit_visual_package"
    if annotations["openWorldHint"] != expected_open_world:
        raise RuntimeError(f"{tool.name} has incorrect openWorldHint")
    if not descriptor.get("title"):
        raise RuntimeError(f"{tool.name} missing human-readable title")
    if not descriptor.get("description") or len(descriptor["description"].strip()) < 60:
        raise RuntimeError(f"{tool.name} description too short")
    output_schema = descriptor.get("outputSchema")
    if not isinstance(output_schema, dict) or output_schema.get("type") != "object":
        raise RuntimeError(f"{tool.name} missing concrete object outputSchema")
    if tool.name == "submit_visual_package":
        meta = descriptor.get("_meta") or descriptor.get("meta") or {}
        if meta.get("openai/fileParams") != ["files"]:
            raise RuntimeError("submit_visual_package missing openai/fileParams metadata")


async def verify() -> None:
    async with streamable_http_client(URL) as streams:
        read_stream, write_stream = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            listed = await session.list_tools()
            tools = {tool.name: tool for tool in listed.tools}
            missing = sorted(REQUIRED - set(tools))
            unexpected = sorted(set(tools) - REQUIRED)
            if missing or unexpected:
                raise RuntimeError(f"MCP tool mismatch; missing={missing}, unexpected={unexpected}")
            for tool in tools.values():
                validate_descriptor(tool)

            result = await session.call_tool(
                "start_writing_task",
                arguments={"prompt": "smoke test only; do not research or draft"},
            )
            if result.is_error:
                raise RuntimeError(f"start_writing_task failed: {result.content}")
            structured = result.structured_content
            if not isinstance(structured, dict):
                raise RuntimeError(f"structured output missing: {structured!r}")
            if structured.get("current_stage") != "RESEARCH" or not structured.get("task_id"):
                raise RuntimeError(f"unexpected start result: {structured}")
            print(f"PASS: {len(tools)} typed/annotated MCP tools exposed and structured start result validated")


def main() -> None:
    env = os.environ.copy()
    env["FINANCIAL_WRITING_DATA_DIR"] = tempfile.mkdtemp(prefix="financial-writing-mcp-")
    env["FINANCIAL_WRITING_REQUIRE_RENDER"] = "0"
    env["MCP_HOST"] = "127.0.0.1"
    env["MCP_PORT"] = str(PORT)
    proc = subprocess.Popen(
        [sys.executable, "-m", "financial_writing_agent.plugin_server"],
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
