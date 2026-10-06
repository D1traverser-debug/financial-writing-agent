from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .network_safety import validate_public_https_url


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
    new_fact: str = Field(min_length=1)
    main_transmission: str = Field(min_length=1)
    likely_reader_misjudgment: str = Field(min_length=1)
    core_contradictions: list[str] = Field(min_length=1, max_length=3)
    comparison_dimensions: list[str] = Field(min_length=1)
    compression_candidates: list[str] = Field(default_factory=list)
    finance_wide_question: str = Field(min_length=1)


class StructureCandidate(StrictModel):
    name: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    sections: list[str] = Field(min_length=2)


class EditorialPlan(StrictModel):
    topic_dna: TopicDNA
    candidates: list[StructureCandidate] = Field(min_length=2)
    selected_structure: StructureCandidate
    finance_deep_emphasis: list[str] = Field(default_factory=list)
    finance_broad_emphasis: list[str] = Field(default_factory=list)
    side_focus_statement: str = Field(min_length=1)
    wechat_sticker_emphasis: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def selected_must_be_unique_candidate(self):
        names = [candidate.name for candidate in self.candidates]
        if len(names) != len(set(names)):
            raise ValueError("candidate structure names must be unique")
        matches = [candidate for candidate in self.candidates if candidate.name == self.selected_structure.name]
        if len(matches) != 1:
            raise ValueError("selected_structure must identify exactly one candidate")
        if matches[0].model_dump() != self.selected_structure.model_dump():
            raise ValueError("selected_structure must exactly match the named candidate")
        return self


class HeadlineCandidate(StrictModel):
    title: str = Field(min_length=1)
    angle: str = Field(min_length=1)
    finance_relevance: str = Field(min_length=1)
    primary_gap: str = Field(min_length=1)
    cognitive_load: Literal["low", "medium", "high"]


class HeadlinePackage(StrictModel):
    finance_deep_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    finance_broad_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    finance_deep_selected: str | None = None
    finance_broad_selected: str | None = None
    wechat_sticker_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    wechat_sticker_selected: str | None = None

    @model_validator(mode="after")
    def candidate_sets_are_unambiguous(self):
        for selected, candidates, label in [
            (self.finance_deep_selected, self.finance_deep_candidates, "finance_deep"),
            (self.finance_broad_selected, self.finance_broad_candidates, "finance_broad"),
            (self.wechat_sticker_selected, self.wechat_sticker_candidates, "wechat_sticker"),
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

    @model_validator(mode="after")
    def risk_section_is_deterministic(self):
        if any("风险提示" in block.text and "免责声明" in block.text for block in self.blocks):
            raise ValueError("do not embed the risk/disclaimer section in blocks; use risk_disclaimer")
        return self


class PlatformConstraintSnapshot(StrictModel):
    platform: str = "微信贴图"
    verified_at: datetime
    source_refs: list[str] = Field(min_length=1)
    title_max_chars: int | None = Field(default=None, ge=1)
    body_max_chars: int | None = Field(default=None, ge=1)
    image_max_count: int | None = Field(default=None, ge=1)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def verification_must_be_current(self):
        verified = self.verified_at
        if verified.tzinfo is None:
            raise ValueError("verified_at must include a timezone")
        now = datetime.now(timezone.utc)
        age = now - verified.astimezone(timezone.utc)
        if age < timedelta(minutes=-15):
            raise ValueError("verified_at cannot be materially in the future")
        if age > timedelta(hours=48):
            raise ValueError("platform constraint snapshot is stale; reverify the current publisher UI/mechanics")
        return self


class StickerPostPayload(StrictModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    interaction_prompt: str = ""
    risk_disclaimer: str = Field(min_length=60)
    constraints: PlatformConstraintSnapshot
    stock_names: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_verified_limits(self):
        if self.constraints.title_max_chars is not None and len(self.title) > self.constraints.title_max_chars:
            raise ValueError("sticker title exceeds verified platform limit")
        publish_body = "\n".join(x for x in [self.body, self.interaction_prompt, self.risk_disclaimer] if x.strip())
        if self.constraints.body_max_chars is not None and len(publish_body) > self.constraints.body_max_chars:
            raise ValueError("sticker publish body exceeds verified platform limit")
        return self


class DraftPackage(StrictModel):
    finance_deep: ArticlePayload | None = None
    finance_broad: ArticlePayload | None = None
    wechat_sticker_post: StickerPostPayload | None = None


class OpenAIFileRef(StrictModel):
    download_url: str = Field(min_length=1)
    file_id: str = Field(min_length=1)
    mime_type: str | None = None
    file_name: str | None = None

    @field_validator("download_url")
    @classmethod
    def download_url_must_be_public_https(cls, value: str) -> str:
        return validate_public_https_url(value)


class VisualAsset(StrictModel):
    article_mode: Literal["FINANCE_DEEP", "FINANCE_BROAD", "WECHAT_STICKER_POST"]
    role: Literal["hero", "section", "sticker"]
    semantic_focus: str = Field(min_length=1)
    file_id: str = Field(min_length=1)
    anchor_after_block: int | None = Field(default=None, ge=0)
    hook_text: str = ""
    aspect_ratio: str = Field(min_length=3)
    avatar_included: bool = True


class VisualPackage(StrictModel):
    assets: list[VisualAsset] = Field(min_length=1)
    avatar_required: bool = True
    target_chars_per_section_image: int = Field(default=700, ge=200, le=2000)
    planning_notes: list[str] = Field(default_factory=list)


class ResolvedVisualAsset(VisualAsset):
    local_path: str = Field(min_length=1)


class ResolvedVisualPackage(StrictModel):
    assets: list[ResolvedVisualAsset] = Field(min_length=1)
    avatar_required: bool = True
    target_chars_per_section_image: int = Field(default=700, ge=200, le=2000)
    planning_notes: list[str] = Field(default_factory=list)


class StyleAuditRubric(StrictModel):
    template_fingerprint: Literal["PASS", "REVISE"]
    transition_continuity: Literal["PASS", "REVISE"]
    repetition_control: Literal["PASS", "REVISE"]
    rhythm_naturalness: Literal["PASS", "REVISE"]
    extreme_language_control: Literal["PASS", "REVISE"]


class StyleAuditDecision(StrictModel):
    status: Literal["PASS", "REVISE"]
    evidence: list[str] = Field(min_length=1)
    rubric: StyleAuditRubric
    detected_patterns: list[str] = Field(default_factory=list)
    transition_findings: list[str] = Field(default_factory=list)
    extreme_language_findings: list[str] = Field(default_factory=list)
    revision_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_matches_rubric(self):
        rubric_values = self.rubric.model_dump().values()
        expected = "PASS" if all(value == "PASS" for value in rubric_values) else "REVISE"
        if self.status != expected:
            raise ValueError(f"style status must be {expected} for the supplied rubric")
        if self.status == "REVISE" and not self.revision_notes:
            raise ValueError("REVISE style audit requires revision_notes")
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
