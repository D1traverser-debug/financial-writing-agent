"""Direct contract tests for the single Financial stage graph and revision map."""
import pytest

from financial_writing_agent.models import Stage
from financial_writing_agent.workflow_spec import (
    BUSINESS_STAGE_ORDER,
    BUSINESS_STAGE_NAMES,
    PASS_TARGET,
    RECOVERABLE_STAGES,
    REVISION_TARGETS,
    REVISION_INVALIDATION_TARGETS,
    STAGE_GATE_NAMES,
    invalidated_gate_names_from,
    invalidated_stage_names_from,
    invalidated_stages_from,
    legal_transitions,
    pass_target,
    pass_target_name,
    require_revision_target,
    revision_target_allowed,
    revision_targets,
)


def test_forward_graph_is_total_and_has_only_one_terminal_edge():
    assert tuple(stage.value for stage in BUSINESS_STAGE_ORDER) == BUSINESS_STAGE_NAMES
    assert len(BUSINESS_STAGE_ORDER) == 10
    for stage in BUSINESS_STAGE_ORDER[:-1]:
        assert pass_target(stage) == PASS_TARGET[stage]
        assert pass_target_name(stage.value) == PASS_TARGET[stage].value
    assert pass_target(Stage.FINAL_AUDIT) == Stage.COMPLETE
    assert pass_target_name("FINAL_AUDIT") == "COMPLETE"
    assert pass_target(Stage.COMPLETE) is None
    assert pass_target(Stage.BLOCKED) is None
    assert pass_target_name("NOT_A_STAGE") is None


def test_revision_map_and_revision_target_admission_are_closed():
    for stage in Stage:
        assert revision_targets(stage) == REVISION_TARGETS.get(stage, frozenset())
        for target in Stage:
            assert revision_target_allowed(stage, target) == (target in revision_targets(stage))
    for stage, targets in REVISION_TARGETS.items():
        for target in targets:
            assert require_revision_target(stage, target.value) is target
    with pytest.raises(ValueError, match="unknown revision target"):
        require_revision_target(Stage.DRAFT, "NOT_A_STAGE")
    with pytest.raises(ValueError, match="unsupported revision target"):
        require_revision_target(Stage.INTAKE, Stage.RESEARCH.value)


def test_legal_transition_graph_contains_only_forward_block_and_declared_revision_edges():
    graph = legal_transitions()
    assert set(graph) == set(Stage)
    for stage in BUSINESS_STAGE_ORDER:
        assert Stage.BLOCKED in graph[stage]
        forward = pass_target(stage)
        if forward is not None:
            assert forward in graph[stage]
        assert revision_targets(stage).issubset(graph[stage])
    assert graph[Stage.COMPLETE] == frozenset()
    assert graph[Stage.BLOCKED] == RECOVERABLE_STAGES
    assert Stage.INTAKE not in REVISION_INVALIDATION_TARGETS
    assert Stage.COMPLETE not in REVISION_INVALIDATION_TARGETS


def test_revision_invalidation_replays_from_the_earliest_allowed_business_stage():
    for target in REVISION_INVALIDATION_TARGETS:
        index = BUSINESS_STAGE_ORDER.index(target)
        expected = BUSINESS_STAGE_ORDER[index:]
        assert invalidated_stages_from(target) == expected
        assert invalidated_stage_names_from(target.value) == tuple(
            stage.value for stage in expected
        )
        expected_gates = tuple(
            gate for stage in expected for gate in STAGE_GATE_NAMES.get(stage, ())
        )
        assert invalidated_gate_names_from(target) == expected_gates


@pytest.mark.parametrize("target", [Stage.INTAKE, Stage.RESEARCH_AUDIT, Stage.COMPLETE, Stage.BLOCKED])
def test_non_revision_stages_cannot_be_used_as_invalidation_roots(target):
    with pytest.raises(ValueError, match="unsupported revision invalidation target"):
        invalidated_stages_from(target)


def test_unknown_revision_stage_name_is_rejected_before_invalidation():
    with pytest.raises(ValueError, match="unknown revision invalidation target"):
        invalidated_stage_names_from("NOT_A_STAGE")
