from __future__ import annotations

import argparse
import json

from .routing import build_task_contract
from .runtime_factory import build_runtime


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="financial-write",
        description="Developer diagnostic runner. Production ChatGPT use should go through the MCP plugin.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="start a new local diagnostic formal financial-writing run")
    run.add_argument("prompt")
    run.add_argument("--source", action="append", default=[])
    run.add_argument("--platform", action="append", default=[])
    run.add_argument("--state-db", default="financial_writing_state.db")
    run.add_argument("--runs-dir", default="runs")
    run.add_argument("--model", default=None)
    run.add_argument("--no-render", action="store_true")

    resume = sub.add_parser("resume", help="resume a checkpointed local diagnostic run")
    resume.add_argument("task_id")
    resume.add_argument("--state-db", default="financial_writing_state.db")
    resume.add_argument("--runs-dir", default="runs")
    resume.add_argument("--model", default=None)
    resume.add_argument("--no-render", action="store_true")

    args = ap.parse_args()
    runtime = build_runtime(
        state_db=args.state_db,
        runs_dir=args.runs_dir,
        model=args.model,
        require_render=not args.no_render,
    )
    if args.cmd == "run":
        contract = build_task_contract(
            prompt=args.prompt,
            source_refs=args.source,
            target_platforms=args.platform,
        )
        state = runtime.start(contract)
    else:
        state = runtime.resume(args.task_id)
    state = runtime.run(state)
    print(json.dumps(state.model_dump(mode="json"), ensure_ascii=False, indent=2))
    if state.stage.value == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
