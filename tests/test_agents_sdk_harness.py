from __future__ import annotations

import json

from pydantic import BaseModel


def test_agents_sdk_scripted_model_drives_structured_stage_without_network():
    from agents import Agent, RunConfig, Runner
    from agents.testing import ScriptedModel, assistant_message

    class Output(BaseModel):
        verdict: str
        evidence: list[str]

    model = ScriptedModel(
        [
            [
                assistant_message(
                    json.dumps(
                        {
                            "verdict": "PASS",
                            "evidence": ["deterministic scripted final output"],
                        }
                    )
                )
            ]
        ]
    )
    agent = Agent(
        name="Financial Writing Deterministic Harness Test",
        instructions="Return the structured result.",
        model=model,
        output_type=Output,
    )
    result = Runner.run_sync(
        agent,
        "Run deterministic test.",
        max_turns=2,
        run_config=RunConfig(
            workflow_name="Financial Writing Agent Test",
            group_id="scripted-model-test",
            trace_metadata={"stage": "TEST"},
            trace_include_sensitive_data=False,
            tracing_disabled=True,
        ),
    )
    assert isinstance(result.final_output, Output)
    assert result.final_output.verdict == "PASS"
    assert result.final_output.evidence == ["deterministic scripted final output"]
    model.assert_complete()
