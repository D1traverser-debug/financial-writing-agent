from __future__ import annotations

from .models import ContentMode, DistributionMode, GateStatus, WritingState
from .schemas import (
    ArticlePayload,
    DraftPackage,
    EditorialPlan,
    HeadlineCandidate,
    HeadlinePackage,
    ModeAcceptanceContract,
    ModeEditorialPlan,
    ResearchPackage,
    WritingAcceptanceContract,
)


SOURCE_COMPLETION_STATES = ("FULL", "PARTIAL", "UNAVAILABLE")


def _validate_task_source_completion(state: WritingState, research: ResearchPackage) -> list[str]:
    refs = list(dict.fromkeys(state.contract.source_refs))
    if not refs:
        return ["task_source_refs=0"]

    boundary = research.source_boundary
    missing: list[str] = []
    for ref in refs:
        if not any(f"[{status}] {ref}" in boundary for status in SOURCE_COMPLETION_STATES):
            missing.append(ref)
    if missing:
        raise ValueError(
            "ResearchPackage.source_boundary must account for every TaskContract source_ref using "
            "'[FULL] <ref>', '[PARTIAL] <ref>' or '[UNAVAILABLE] <ref>'; "
            f"missing={missing}"
        )
    return [f"task_source_refs={len(refs)}; source_completion=accounted"]


def validate_research_against_knowledge_context(state: WritingState, research: ResearchPackage) -> list[str]:
    evidence = _validate_task_source_completion(state, research)
    gate = state.gates.get("knowledge_context")
    if gate is None or gate.status not in {GateStatus.PASS, GateStatus.N_A}:
        raise ValueError("knowledge_context must be PASS or N_A before research validation")

    recorded = set(state.working.get("knowledge_context_refs") or [])
    claimed = set(research.cognition.prior_knowledge_refs)

    if gate.status == GateStatus.N_A:
        if claimed:
            raise ValueError(
                "ResearchPackage.cognition.prior_knowledge_refs must be empty when knowledge_context=N_A"
            )
        evidence.append("knowledge_context=N_A; prior_knowledge_refs=0")
        return evidence

    if not recorded:
        raise ValueError("knowledge_context=PASS requires recorded durable-knowledge references")
    invented = sorted(claimed - recorded)
    if invented:
        raise ValueError(
            f"ResearchPackage claims prior_knowledge_refs not recorded by knowledge_context: {invented}"
        )
    evidence.append(
        f"knowledge_context=PASS; retrieved_refs={len(recorded)}; reused_refs={len(claimed)}"
    )
    return evidence


def _validated_anchor_claims(state: WritingState) -> set[str]:
    raw_research = state.working.get("research")
    if raw_research is None:
        raise ValueError("headline validation requires frozen ResearchPackage")
    research = ResearchPackage.model_validate(raw_research)
    return {item.claim.strip() for item in research.evidence_ledger if item.core_safe}


def _validate_headline_candidate_anchors(
    state: WritingState,
    candidates: list[HeadlineCandidate],
    *,
    label: str,
) -> None:
    safe_claims = _validated_anchor_claims(state)
    missing = [candidate.title for candidate in candidates if candidate.factual_anchor.strip() not in safe_claims]
    if missing:
        raise ValueError(
            f"{label} headline factual_anchor must exactly match a core_safe ResearchPackage evidence claim; "
            f"invalid_titles={missing}"
        )


def _selected_candidate(candidates: list[HeadlineCandidate], selected_title: str) -> HeadlineCandidate:
    matches = [candidate for candidate in candidates if candidate.title == selected_title]
    if len(matches) != 1:
        raise ValueError("selected headline must identify exactly one candidate")
    return matches[0]


def _mode_contract(
    plan: ModeEditorialPlan,
    selected_title: str,
    selected_candidate: HeadlineCandidate,
    *,
    require_section_expectations: bool,
) -> ModeAcceptanceContract:
    if require_section_expectations and not plan.section_expectations:
        raise ValueError(
            "formal article acceptance contract requires section_expectations for every selected H1"
        )
    return ModeAcceptanceContract(
        selected_title=selected_title,
        headline_factual_anchor=selected_candidate.factual_anchor,
        headline_primary_gap=selected_candidate.primary_gap,
        headline_opening_payoff=selected_candidate.opening_payoff,
        selected_structure_name=plan.selected_structure.name,
        expected_h1_count=len(plan.selected_structure.sections),
        expected_section_functions=plan.selected_structure.sections,
        section_expectations=plan.section_expectations,
        side_focus_statement=plan.side_focus_statement,
        company_selection_basis=plan.company_selection_basis,
    )


def freeze_acceptance_contract(state: WritingState) -> WritingAcceptanceContract:
    editorial = EditorialPlan.model_validate(state.working["editorial_plan"])
    headlines = HeadlinePackage.model_validate(state.working["headlines"])

    deep = None
    broad = None
    sticker = None
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        if editorial.wechat_sticker is None or not headlines.wechat_sticker_selected:
            raise ValueError("WECHAT_STICKER_POST acceptance contract requires frozen editorial plan and selected title")
        _validate_headline_candidate_anchors(
            state,
            headlines.wechat_sticker_candidates,
            label="WECHAT_STICKER_POST",
        )
        candidate = _selected_candidate(
            headlines.wechat_sticker_candidates,
            headlines.wechat_sticker_selected,
        )
        sticker = _mode_contract(
            editorial.wechat_sticker,
            headlines.wechat_sticker_selected,
            candidate,
            require_section_expectations=False,
        )
    else:
        if state.contract.distribution_mode in {DistributionMode.FINANCE_DEEP, DistributionMode.DUAL}:
            if editorial.finance_deep is None or not headlines.finance_deep_selected:
                raise ValueError("FINANCE_DEEP acceptance contract requires frozen editorial plan and selected title")
            _validate_headline_candidate_anchors(
                state,
                headlines.finance_deep_candidates,
                label="FINANCE_DEEP",
            )
            candidate = _selected_candidate(
                headlines.finance_deep_candidates,
                headlines.finance_deep_selected,
            )
            deep = _mode_contract(
                editorial.finance_deep,
                headlines.finance_deep_selected,
                candidate,
                require_section_expectations=True,
            )
        if state.contract.distribution_mode in {DistributionMode.FINANCE_BROAD, DistributionMode.DUAL}:
            if editorial.finance_broad is None or not headlines.finance_broad_selected:
                raise ValueError("FINANCE_BROAD acceptance contract requires frozen editorial plan and selected title")
            _validate_headline_candidate_anchors(
                state,
                headlines.finance_broad_candidates,
                label="FINANCE_BROAD",
            )
            candidate = _selected_candidate(
                headlines.finance_broad_candidates,
                headlines.finance_broad_selected,
            )
            broad = _mode_contract(
                editorial.finance_broad,
                headlines.finance_broad_selected,
                candidate,
                require_section_expectations=True,
            )

    contract = WritingAcceptanceContract(
        finance_deep=deep,
        finance_broad=broad,
        wechat_sticker=sticker,
        required_outputs=[kind.value for kind in state.contract.required_outputs],
        delivery_channel=state.contract.delivery_channel.value,
        visuals_enabled=state.contract.visuals_enabled,
    )
    state.working["acceptance_contract"] = contract.model_dump(mode="json")
    state.set_gate(
        "acceptance_contract",
        GateStatus.PASS,
        [
            f"required_outputs={len(contract.required_outputs)}",
            f"finance_deep={'yes' if contract.finance_deep else 'no'}",
            f"finance_broad={'yes' if contract.finance_broad else 'no'}",
            f"wechat_sticker={'yes' if contract.wechat_sticker else 'no'}",
            "all headline factual anchors exactly match core_safe research claims",
            "formal H1 direction/gap/payoff/hierarchy expectations frozen",
            "selected headline factual anchor/gap/opening payoff frozen per applicable mode",
        ],
    )
    return contract


def _article_sections(article: ArticlePayload) -> list[tuple[str, list]]:
    sections: list[tuple[str, list]] = []
    current_title: str | None = None
    current_children: list = []
    for block in article.blocks:
        if block.kind == "lead":
            continue
        if block.kind == "h1":
            if current_title is not None:
                sections.append((current_title, current_children))
            current_title = block.text
            current_children = []
            continue
        if current_title is None:
            raise ValueError("article content appears before the first H1")
        current_children.append(block)
    if current_title is not None:
        sections.append((current_title, current_children))
    return sections


def _validate_section_hierarchy(label: str, article: ArticlePayload, expected: ModeAcceptanceContract) -> list[str]:
    if not expected.section_expectations:
        raise ValueError(f"{label} frozen acceptance contract is missing section_expectations")
    sections = _article_sections(article)
    if len(sections) != len(expected.section_expectations):
        raise ValueError(
            f"{label} section count differs from section acceptance contract: "
            f"actual={len(sections)}, expected={len(expected.section_expectations)}"
        )

    evidence: list[str] = []
    for section_index, (spec, actual) in enumerate(zip(expected.section_expectations, sections), start=1):
        actual_h1, children = actual
        if actual_h1 != spec.h1_title:
            raise ValueError(
                f"{label} H1[{section_index}] differs from section acceptance contract: "
                f"actual={actual_h1!r}, expected={spec.h1_title!r}"
            )

        actual_h2 = [block.text for block in children if block.kind == "h2"]
        expected_h2 = spec.logical_blocks if len(spec.logical_blocks) >= 2 else []
        if actual_h2 != expected_h2:
            raise ValueError(
                f"{label} H1[{section_index}] H2 hierarchy differs from frozen logical blocks: "
                f"actual={actual_h2}, expected={expected_h2}"
            )

        h3_counts: dict[int, int] = {index: 0 for index in range(1, len(actual_h2) + 1)}
        current_h2 = 0
        for block in children:
            if block.kind == "h2":
                current_h2 += 1
            elif block.kind == "h3":
                if current_h2 == 0:
                    raise ValueError(f"{label} H1[{section_index}] contains H3 before any H2")
                h3_counts[current_h2] += 1

        required_h3 = set(spec.h3_required_h2_indexes)
        for h2_index, count in h3_counts.items():
            if h2_index in required_h3 and count < 3:
                raise ValueError(
                    f"{label} H1[{section_index}] H2[{h2_index}] requires at least 3 H3 units; actual={count}"
                )
            if h2_index not in required_h3 and count:
                raise ValueError(
                    f"{label} H1[{section_index}] H2[{h2_index}] has unexpected H3 hierarchy; "
                    "revise the section contract instead of drifting during drafting"
                )

        evidence.append(
            f"{label}.H1_{section_index}: direction/gap/payoff=frozen; "
            f"logical_blocks={len(spec.logical_blocks)}; h2={len(actual_h2)}; "
            f"h3_required={sorted(required_h3)}"
        )
    return evidence


def validate_draft_against_acceptance(state: WritingState, draft: DraftPackage) -> list[str]:
    contract = WritingAcceptanceContract.model_validate(state.working.get("acceptance_contract"))
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        expected = contract.wechat_sticker
        article = draft.wechat_sticker_post
        if expected is None or article is None:
            raise ValueError("WECHAT_STICKER_POST draft missing against frozen acceptance contract")
        if article.title != expected.selected_title:
            raise ValueError("WECHAT_STICKER_POST draft title differs from frozen selected title")
        return ["WECHAT_STICKER_POST: title=frozen; headline promises=frozen; platform-specific body contract"]

    evidence: list[str] = []
    for label, expected, article in [
        ("FINANCE_DEEP", contract.finance_deep, draft.finance_deep),
        ("FINANCE_BROAD", contract.finance_broad, draft.finance_broad),
    ]:
        if expected is None:
            continue
        if article is None:
            raise ValueError(f"{label} draft missing against acceptance contract")
        if article.title != expected.selected_title:
            raise ValueError(f"{label} draft title differs from frozen selected title")
        actual_h1 = [block.text for block in article.blocks if block.kind == "h1"]
        if len(actual_h1) != expected.expected_h1_count:
            raise ValueError(
                f"{label} H1 count differs from frozen structure: actual={len(actual_h1)}, expected={expected.expected_h1_count}"
            )
        if actual_h1 != expected.expected_section_functions:
            raise ValueError(
                f"{label} H1 sequence differs from frozen structure: actual={actual_h1}, expected={expected.expected_section_functions}"
            )
        hierarchy_evidence = _validate_section_hierarchy(label, article, expected)
        evidence.append(
            f"{label}: lead=1; h1={len(actual_h1)}; title=frozen; h1_sequence=frozen; headline_promises=frozen"
        )
        evidence.extend(hierarchy_evidence)
    return evidence
