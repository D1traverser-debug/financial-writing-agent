from __future__ import annotations

from .models import Stage

# Canonical Financial business sequence. Execution adapters may narrow what they can
# certify, but they must not invent broader stage/revision paths outside this graph.
BUSINESS_STAGE_ORDER: tuple[Stage, ...] = (
    Stage.INTAKE,
    Stage.RESEARCH,
    Stage.RESEARCH_AUDIT,
    Stage.EDITORIAL,
    Stage.TITLE,
    Stage.DRAFT,
    Stage.EDITORIAL_AUDIT,
    Stage.DELIVERY,
    Stage.MECHANICAL_AUDIT,
    Stage.FINAL_AUDIT,
)
BUSINESS_STAGE_NAMES: tuple[str, ...] = tuple(stage.value for stage in BUSINESS_STAGE_ORDER)
RECOVERABLE_STAGES = frozenset(BUSINESS_STAGE_ORDER)

# PASS/normal forward route. FINAL_AUDIT reaches the owner-native terminal stage;
# bounded adapters such as GITHUB_CHAT may translate that edge into their weaker
# terminal status without claiming Stage.COMPLETE.
PASS_TARGET: dict[Stage, Stage] = {
    Stage.INTAKE: Stage.RESEARCH,
    Stage.RESEARCH: Stage.RESEARCH_AUDIT,
    Stage.RESEARCH_AUDIT: Stage.EDITORIAL,
    Stage.EDITORIAL: Stage.TITLE,
    Stage.TITLE: Stage.DRAFT,
    Stage.DRAFT: Stage.EDITORIAL_AUDIT,
    Stage.EDITORIAL_AUDIT: Stage.DELIVERY,
    Stage.DELIVERY: Stage.MECHANICAL_AUDIT,
    Stage.MECHANICAL_AUDIT: Stage.FINAL_AUDIT,
    Stage.FINAL_AUDIT: Stage.COMPLETE,
}

# Legal revision targets owned by the business workflow, not by an execution adapter.
# A specific adapter may expose only a subset when its assurance/executor cannot
# support every route, but it may never add a target outside this map.
REVISION_TARGETS: dict[Stage, frozenset[Stage]] = {
    Stage.RESEARCH_AUDIT: frozenset({Stage.RESEARCH}),
    Stage.TITLE: frozenset({Stage.TITLE}),
    Stage.DRAFT: frozenset({Stage.DRAFT}),
    Stage.EDITORIAL_AUDIT: frozenset({Stage.RESEARCH, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT}),
    Stage.MECHANICAL_AUDIT: frozenset({Stage.DELIVERY}),
    Stage.FINAL_AUDIT: frozenset({Stage.RESEARCH, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT, Stage.DELIVERY}),
}

REVIEW_STAGES = frozenset(
    {
        Stage.RESEARCH_AUDIT,
        Stage.EDITORIAL_AUDIT,
        Stage.MECHANICAL_AUDIT,
        Stage.FINAL_AUDIT,
    }
)
REVIEW_STAGE_NAMES = frozenset(stage.value for stage in REVIEW_STAGES)

# Gate ownership by stage lets downstream invalidation derive its dependency set
# from one stage graph instead of hand-maintaining a second list of gate names.
STAGE_GATE_NAMES: dict[Stage, tuple[str, ...]] = {
    Stage.RESEARCH: ("research_output",),
    Stage.RESEARCH_AUDIT: ("research_audit",),
    Stage.EDITORIAL: ("editorial_plan",),
    Stage.TITLE: ("title_audit",),
    Stage.DRAFT: ("draft_output",),
    Stage.EDITORIAL_AUDIT: ("hook_audit", "style_audit", "editorial_audit"),
    Stage.DELIVERY: ("delivery_output",),
    Stage.MECHANICAL_AUDIT: ("mechanical_audit",),
    Stage.FINAL_AUDIT: ("final_audit",),
}

# Revisions are only meaningful from these business stages. INTAKE cannot be a
# revision target and FINAL_AUDIT cannot revise to another audit stage directly.
REVISION_INVALIDATION_TARGETS = frozenset(
    {Stage.RESEARCH, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT, Stage.DELIVERY}
)


def pass_target(stage: Stage) -> Stage | None:
    return PASS_TARGET.get(stage)


def pass_target_name(stage_name: str) -> str | None:
    try:
        target = pass_target(Stage(stage_name))
    except ValueError:
        return None
    return target.value if target is not None else None


def revision_targets(stage: Stage) -> frozenset[Stage]:
    return REVISION_TARGETS.get(stage, frozenset())


def revision_target_allowed(stage: Stage, target: Stage) -> bool:
    return target in revision_targets(stage)


def require_revision_target(stage: Stage, target: str) -> Stage:
    try:
        target_stage = Stage(target)
    except ValueError as exc:
        raise ValueError(f"unknown revision target: {target}") from exc
    if not revision_target_allowed(stage, target_stage):
        allowed = ",".join(sorted(item.value for item in revision_targets(stage))) or "NONE"
        raise ValueError(f"unsupported revision target for {stage.value}: {target}; allowed={allowed}")
    return target_stage


def legal_transitions() -> dict[Stage, frozenset[Stage]]:
    graph: dict[Stage, frozenset[Stage]] = {}
    for stage in BUSINESS_STAGE_ORDER:
        targets: set[Stage] = {Stage.BLOCKED}
        forward = pass_target(stage)
        if forward is not None:
            targets.add(forward)
        targets.update(revision_targets(stage))
        graph[stage] = frozenset(targets)
    graph[Stage.COMPLETE] = frozenset()
    graph[Stage.BLOCKED] = RECOVERABLE_STAGES
    return graph


LEGAL_TRANSITIONS = legal_transitions()


def invalidated_stages_from(target: Stage) -> tuple[Stage, ...]:
    if target not in REVISION_INVALIDATION_TARGETS:
        raise ValueError(f"unsupported revision invalidation target: {target.value}")
    start = BUSINESS_STAGE_ORDER.index(target)
    return BUSINESS_STAGE_ORDER[start:]


def invalidated_stage_names_from(target_name: str) -> tuple[str, ...]:
    try:
        target = Stage(target_name)
    except ValueError as exc:
        raise ValueError(f"unknown revision invalidation target: {target_name}") from exc
    return tuple(stage.value for stage in invalidated_stages_from(target))


def invalidated_gate_names_from(target: Stage) -> tuple[str, ...]:
    names: list[str] = []
    for stage in invalidated_stages_from(target):
        names.extend(STAGE_GATE_NAMES.get(stage, ()))
    return tuple(names)
