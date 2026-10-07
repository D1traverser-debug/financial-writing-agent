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
    sticker = None
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        if editorial.wechat_sticker is None or not headlines.wechat_sticker_selected:
            raise ValueError("WECHAT_STICKER_POST acceptance contract requires frozen editorial plan and selected title")
        sticker = _mode_contract(editorial.wechat_sticker, headlines.wechat_sticker_selected)
    else:
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
        ],
    )
    return contract


def validate_draft_against_acceptance(state: WritingState, draft: DraftPackage) -> list[str]:
    contract = WritingAcceptanceContract.model_validate(state.working.get("acceptance_contract"))
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        expected = contract.wechat_sticker
        article = draft.wechat_sticker_post
        if expected is None or article is None:
            raise ValueError("WECHAT_STICKER_POST draft missing against frozen acceptance contract")
        if article.title != expected.selected_title:
            raise ValueError("WECHAT_STICKER_POST draft title differs from frozen selected title")
        return ["WECHAT_STICKER_POST: title=frozen; platform-specific body contract"]

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
        evidence.append(f"{label}: lead=1; h1={len(actual_h1)}; title=frozen; h1_sequence=frozen")
    return evidence
