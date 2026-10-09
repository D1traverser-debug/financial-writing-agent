from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EvidenceItem(StrictModel):
    claim: str = Field(min_length=1)
    source: str = Field(min_length=1)
    date: str | None = None
    evidence_type: str = "web"
    confidence: Literal["high", "medium", "low"] = "medium"
    core_safe: bool = False
    notes: str = ""


class CompanyFinding(StrictModel):
    name: str = Field(min_length=1)
    ticker: str | None = None
    relevance: str = Field(min_length=1)
    business_stage: str = ""
    positive_evidence: list[str] = Field(default_factory=list)
    negative_evidence: list[str] = Field(default_factory=list)
    why_this: str = ""
    why_not: list[str] = Field(default_factory=list)
    market_role: str = ""
    short_term_role: str = ""
    positioning_signals: list[str] = Field(default_factory=list)
    fund_flow_signals: list[str] = Field(default_factory=list)


class MarketCognition(StrictModel):
    prior_knowledge_refs: list[str] = Field(default_factory=list)
    concept_map: list[str] = Field(min_length=1)
    adjacent_or_competing_concepts: list[str] = Field(default_factory=list)
    industry_logic: list[str] = Field(min_length=1)
    short_term_market_structure: list[str] = Field(default_factory=list)
    knowledge_conflicts: list[str] = Field(default_factory=list)


class ResearchCoverage(StrictModel):
    sweeps_completed: int = Field(ge=2, le=10)
    coverage_status: Literal["SATURATED", "BOUNDED_WITH_GAPS"]
    material_new_items_last_sweep: int = Field(ge=0)
    concept_coverage: str = Field(min_length=1)
    company_coverage: str = Field(min_length=1)
    source_diversity: str = Field(min_length=1)
    excluded_scope: list[str] = Field(default_factory=list)
    stop_reason: str = Field(min_length=1)


class ResearchPackage(StrictModel):
    topic: str = Field(min_length=1)
    chronology: list[str] = Field(min_length=1)
    what_changed: list[str] = Field(min_length=1)
    industry_chain: list[str] = Field(min_length=1)
    transmission_chain: list[str] = Field(min_length=1)
    universe: list[CompanyFinding] = Field(default_factory=list)
    evidence_ledger: list[EvidenceItem] = Field(min_length=1)
    counterevidence: list[str] = Field(default_factory=list)
    unresolved_gaps: list[str] = Field(default_factory=list)
    provisional_theses: list[str] = Field(min_length=1)
    source_boundary: str = Field(min_length=1)
    cognition: MarketCognition
    coverage: ResearchCoverage
    knowledge_writeback_candidates: list[str] = Field(default_factory=list)


class TopicDNA(StrictModel):
    """Shared factual/topic DNA. Selection/compression is mode-specific, not shared."""

    new_fact: str = Field(min_length=1)
    main_transmission: str = Field(min_length=1)
    likely_reader_misjudgment: str = Field(min_length=1)
    comparison_dimensions: list[str] = Field(min_length=1)
    finance_wide_question: str = Field(min_length=1)


class StructureCandidate(StrictModel):
    name: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    sections: list[str] = Field(min_length=2)


class ModeEditorialPlan(StrictModel):
    coverage_policy: Literal["MATERIAL_COMPLETE", "SELECTIVE_TRAFFIC"]
    candidates: list[StructureCandidate] = Field(min_length=2)
    selected_structure: StructureCandidate
    emphasis: list[str] = Field(default_factory=list)
    completeness_obligations: list[str] = Field(default_factory=list)
    core_contradictions: list[str] = Field(default_factory=list, max_length=3)
    compression_candidates: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_mode_contract(self):
        names = [candidate.name for candidate in self.candidates]
        if len(names) != len(set(names)):
            raise ValueError("candidate structure names must be unique")
        matches = [candidate for candidate in self.candidates if candidate.name == self.selected_structure.name]
        if len(matches) != 1 or matches[0].model_dump() != self.selected_structure.model_dump():
            raise ValueError("selected_structure must exactly match one candidate")
        if self.coverage_policy == "MATERIAL_COMPLETE":
            if not self.completeness_obligations:
                raise ValueError("MATERIAL_COMPLETE plan requires completeness_obligations")
            if self.core_contradictions or self.compression_candidates:
                raise ValueError("FINANCE_DEEP material-complete plan must not use contradiction/compression selection fields")
        else:
            if not self.core_contradictions:
                raise ValueError("SELECTIVE_TRAFFIC plan requires 1-3 core_contradictions")
        return self


class EditorialPlan(StrictModel):
    topic_dna: TopicDNA
    finance_deep: ModeEditorialPlan | None = None
    finance_broad: ModeEditorialPlan | None = None


class HeadlineCandidate(StrictModel):
    title: str = Field(min_length=1)
    angle: str = Field(min_length=1)
    finance_relevance: str = Field(min_length=1)
    cross_finance_click_reason: str = Field(min_length=1)
    primary_gap: str = Field(min_length=1)
    cognitive_load: Literal["low", "medium", "high"]
    wechat_search_terms: list[str] = Field(min_length=1)
    search_evidence_refs: list[str] = Field(min_length=1)


class HeadlinePackage(StrictModel):
    finance_deep_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    finance_broad_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    finance_deep_selected: str | None = None
    finance_broad_selected: str | None = None

    @model_validator(mode="after")
    def candidate_sets_are_unambiguous(self):
        for selected, candidates, label in [
            (self.finance_deep_selected, self.finance_deep_candidates, "finance_deep"),
            (self.finance_broad_selected, self.finance_broad_candidates, "finance_broad"),
        ]:
            titles = [candidate.title for candidate in candidates]
            if len(titles) != len(set(titles)):
                raise ValueError(f"{label}_candidates must contain unique titles")
            if selected and selected not in set(titles):
                raise ValueError(f"{label}_selected must be one of its candidates")
        return self


class ArticleBlock(StrictModel):
    kind: Literal["lead", "h1", "h2", "h3", "body"]
    text: str = Field(min_length=1)


class ArticlePayload(StrictModel):
    title: str = Field(min_length=1)
    blocks: list[ArticleBlock] = Field(min_length=3)
    risk_disclaimer: str = Field(min_length=60)
    stock_names: list[str] = Field(default_factory=list)
    skim_path_anchors: list[str] = Field(min_length=3)

    @model_validator(mode="after")
    def validate_payload_contract(self):
        if any("风险提示" in block.text and "免责声明" in block.text for block in self.blocks):
            raise ValueError("do not embed the risk/disclaimer section in blocks; use risk_disclaimer")
        full_text = "\n".join(block.text for block in self.blocks)
        for anchor in self.skim_path_anchors:
            if f"**{anchor}**" not in full_text:
                raise ValueError(f"skim_path_anchor must appear as an exact explicit bold span: {anchor}")
        return self


class DraftPackage(StrictModel):
    finance_deep: ArticlePayload | None = None
    finance_broad: ArticlePayload | None = None


class HumanVoiceAuditRubric(StrictModel):
    template_fingerprint: Literal["PASS", "REVISE"]
    transition_continuity: Literal["PASS", "REVISE"]
    repetition_control: Literal["PASS", "REVISE"]
    rhythm_naturalness: Literal["PASS", "REVISE"]
    reader_dialogue: Literal["PASS", "REVISE"]
    narrative_flow: Literal["PASS", "REVISE"]
    judgment_persona: Literal["PASS", "REVISE"]
    extreme_language_control: Literal["PASS", "REVISE"]


class StyleAuditDecision(StrictModel):
    status: Literal["PASS", "REVISE"]
    evidence: list[str] = Field(min_length=1)
    rubric: HumanVoiceAuditRubric
    detected_patterns: list[str] = Field(default_factory=list)
    transition_findings: list[str] = Field(default_factory=list)
    revision_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_matches_rubric(self):
        expected = "PASS" if all(value == "PASS" for value in self.rubric.model_dump().values()) else "REVISE"
        if self.status != expected:
            raise ValueError(f"human-voice status must be {expected} for the supplied rubric")
        if self.status == "REVISE" and not self.revision_notes:
            raise ValueError("REVISE human-voice audit requires revision_notes")
        return self


class HookAuditRubric(StrictModel):
    title_cross_finance_clickability: Literal["PASS", "REVISE"]
    title_wechat_search_intent: Literal["PASS", "REVISE"]
    opening_three_sentence_retention: Literal["PASS", "REVISE"]
    h1_continuation_power: Literal["PASS", "REVISE"]
    paragraph_forward_pull: Literal["PASS", "REVISE"]
    title_opening_payoff: Literal["PASS", "REVISE"]


class HookAuditDecision(StrictModel):
    status: Literal["PASS", "REVISE"]
    evidence: list[str] = Field(min_length=1)
    rubric: HookAuditRubric
    search_terms_checked: list[str] = Field(min_length=1)
    search_evidence_refs: list[str] = Field(min_length=1)
    revision_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_matches_rubric(self):
        expected = "PASS" if all(value == "PASS" for value in self.rubric.model_dump().values()) else "REVISE"
        if self.status != expected:
            raise ValueError(f"hook status must be {expected} for the supplied rubric")
        if self.status == "REVISE" and not self.revision_notes:
            raise ValueError("REVISE hook audit requires revision_notes")
        return self


class GateDecision(StrictModel):
    status: Literal["PASS", "REVISE", "FAIL"]
    evidence: list[str] = Field(min_length=1)
    defects: list[str] = Field(default_factory=list)
    revision_target: Literal["RESEARCH", "EDITORIAL", "TITLE", "DRAFT", "DELIVERY"] | None = None
    remaining_boundaries: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def decision_is_actionable(self):
        if self.status == "REVISE" and self.revision_target is None:
            raise ValueError("REVISE requires revision_target")
        if self.status == "FAIL" and not self.defects:
            raise ValueError("FAIL requires at least one defect")
        return self
