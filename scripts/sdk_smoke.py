from __future__ import annotations

import argparse
import os

from pydantic import BaseModel


class SmokeOutput(BaseModel):
    ok: bool


def structural_smoke() -> None:
    from agents import Agent, RunConfig, Runner, WebSearchTool

    agent = Agent(
        name="Financial Writing Agent SDK Smoke",
        instructions="Return the requested structured output.",
        output_type=SmokeOutput,
        tools=[WebSearchTool(search_context_size="low", external_web_access=True)],
    )
    run_config = RunConfig(
        workflow_name="Financial Writing Agent",
        group_id="structural-smoke-task",
        trace_metadata={"stage": "SMOKE"},
        trace_include_sensitive_data=False,
        tracing_disabled=True,
    )
    if agent.output_type is not SmokeOutput:
        raise RuntimeError("structured output type was not preserved")
    if not callable(Runner.run_sync):
        raise RuntimeError("Runner.run_sync is unavailable")
    if run_config.workflow_name != "Financial Writing Agent" or run_config.group_id != "structural-smoke-task":
        raise RuntimeError("RunConfig workflow/group tracing fields unavailable")
    if run_config.trace_include_sensitive_data is not False:
        raise RuntimeError("trace privacy configuration was not preserved")
    print("PASS: Agents SDK Agent/Runner/WebSearchTool/structured output and task-grouped RunConfig tracing surface")


def live_smoke(model: str | None) -> None:
    from agents import Agent, RunConfig, Runner

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required for --live")
    kwargs = {
        "name": "Financial Writing Agent Live SDK Smoke",
        "instructions": "Return ok=true and nothing else via the structured output.",
        "output_type": SmokeOutput,
    }
    if model:
        kwargs["model"] = model
    agent = Agent(**kwargs)
    result = Runner.run_sync(
        agent,
        "Return ok=true.",
        max_turns=2,
        run_config=RunConfig(
            workflow_name="Financial Writing Agent",
            group_id="live-sdk-smoke",
            trace_metadata={"stage": "LIVE_SMOKE"},
            trace_include_sensitive_data=False,
        ),
    )
    out = result.final_output
    if not isinstance(out, SmokeOutput) or not out.ok:
        raise RuntimeError(f"unexpected live smoke output: {out!r}")
    print(f"PASS: live OpenAI Agents SDK structured-output call using {model or 'SDK default model'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--model", default=os.getenv("FINANCIAL_WRITING_MODEL"))
    args = ap.parse_args()
    structural_smoke()
    if args.live:
        live_smoke(args.model)


if __name__ == "__main__":
    main()
