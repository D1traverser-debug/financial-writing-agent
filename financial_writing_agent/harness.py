from __future__ import annotations

from .models import ContentMode, DistributionMode, GateStatus, WritingState
from .schemas import (
    DraftPackage,
    EditorialPlan,
    HeadlinePackage,
    ModeAcceptanceContract,
    ModeEditorialPlan,
    WritingAcceptanceContract,
)


def _mode_contract(plan: ModeEditorialPlan, selected_title: str) -> ModeAcceptanceContract:
    return ModeAcceptanceContract(
        selected_title=selected_title,
        selected_structure_name=plan.selected_structure.name,
        expected_h1_count=len(plan.selected_structure.sections),
        expected_section_functions=plan.selected_structure.sections,
        side_focus_statement=plan.side_focus_statement,
        company_selection_basis=plan.company_selection_basis,
    )


def freeze_acceptance_contract(state: WritingState) -> WritingAcceptanceContract:
    editorial = EditorialPlan.model_validate(state.working["editorial_plan"])
    headlines = HeadlinePackage.model_validate(state.working["headlines"])

    deep = None
    broad = None
    if state.contract.content_mode != ContentMode.WECHAT_STICKER_POST:
        if state.contract.distribution_mode in {DistributionMode.FINANCE_DEEP, DistributionMode.DUAL}:
            if editorial.finance_deep is None or not headlines.finance_deep_selected:
                raise ValueError("FINANCE_DEEP acceptance contract requires frozen editorial plan and selected title")
            deep = _mode_contract(editorial.finance_deep, headlines.finance_deep_selected)
        if state.contract.distribution_mode in {DistributionMode.FINANCE_BROAD, DistributionMode.DUAL}:
            if editorial.finance_broad is None or not headlines.finance_broad_selected:
                raise ValueError("FINANCE_BROAD acceptance contract requires frozen editorial plan and selected title")
            broad = _mode_contract(editorial.finance_broad, headlines.finance_broad_selected)

    contract = WritingAcceptanceContract(
        finance_deep=deep,
        finance_broad=broad,
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
        ],
    )
    return contract


def validate_draft_against_acceptance(state: WritingState, draft: DraftPackage) -> list[str]:
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        return ["sticker mode uses platform-specific draft contract"]

    contract = WritingAcceptanceContract.model_validate(state.working.get("acceptance_contract"))
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
        h1_count = sum(block.kind == "h1" for block in article.blocks)
        if h1_count != expected.expected_h1_count:
            raise ValueError(
                f"{label} H1 count differs from frozen structure: actual={h1_count}, expected={expected.expected_h1_count}"
            )
        evidence.append(f"{label}: lead=1; h1={h1_count}; title=frozen")
    return evidence
