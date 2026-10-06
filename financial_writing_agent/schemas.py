from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class EvidenceItem(BaseModel):
    claim: str
    source: str
    date: str | None = None
    evidence_type: str = "web"
    confidence: Literal["high", "medium", "low"] = "medium"
    core_safe: bool = False
    notes: str = ""


class CompanyFinding(BaseModel):
    name: str
    ticker: str | None = None
    relevance: str
    business_stage: str = ""
    positive_evidence: list[str] = Field(default_factory=list)
    negative_evidence: list[str] = Field(default_factory=list)
    why_this: str = ""
    why_not: list[str] = Field(default_factory=list)
    market_role: str = ""
    short_term_role: str = ""
    positioning_signals: list[str] = Field(default_factory=list)
    fund_flow_signals: list[str] = Field(default_factory=list)


class MarketCognition(BaseModel):
    prior_knowledge_refs: list[str] = Field(default_factory=list)
    concept_map: list[str] = Field(default_factory=list)
    adjacent_or_competing_concepts: list[str] = Field(default_factory=list)
    industry_logic: list[str] = Field(default_factory=list)
    short_term_market_structure: list[str] = Field(default_factory=list)
    knowledge_conflicts: list[str] = Field(default_factory=list)


class ResearchPackage(BaseModel):
    topic: str
    chronology: list[str]
    what_changed: list[str]
    industry_chain: list[str]
    transmission_chain: list[str]
    universe: list[CompanyFinding]
    evidence_ledger: list[EvidenceItem]
    counterevidence: list[str]
    unresolved_gaps: list[str]
    provisional_theses: list[str]
    source_boundary: str
    cognition: MarketCognition = Field(default_factory=MarketCognition)
    knowledge_writeback_candidates: list[str] = Field(default_factory=list)


class TopicDNA(BaseModel):
    new_fact: str
    main_transmission: str
    likely_reader_misjudgment: str
    core_contradictions: list[str]
    comparison_dimensions: list[str]
    compression_candidates: list[str]
    finance_wide_question: str


class StructureCandidate(BaseModel):
    name: str
    rationale: str
    sections: list[str]


class EditorialPlan(BaseModel):
    topic_dna: TopicDNA
    candidates: list[StructureCandidate]
    selected_structure: StructureCandidate
    finance_deep_emphasis: list[str]
    finance_broad_emphasis: list[str]
    side_focus_statement: str
    wechat_sticker_emphasis: list[str] = Field(default_factory=list)


class HeadlineCandidate(BaseModel):
    title: str
    angle: str
    finance_relevance: str
    primary_gap: str
    cognitive_load: Literal["low", "medium", "high"]


class HeadlinePackage(BaseModel):
    finance_deep_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    finance_broad_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    finance_deep_selected: str | None = None
    finance_broad_selected: str | None = None
    wechat_sticker_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    wechat_sticker_selected: str | None = None


class ArticleBlock(BaseModel):
    kind: Literal["lead", "h1", "h2", "h3", "body"]
    text: str


class ArticlePayload(BaseModel):
    title: str
    blocks: list[ArticleBlock]
    stock_names: list[str] = Field(default_factory=list)


class PlatformConstraintSnapshot(BaseModel):
    platform: str = "微信贴图"
    verified_at: str
    source_refs: list[str] = Field(min_length=1)
    title_max_chars: int | None = Field(default=None, ge=1)
    body_max_chars: int | None = Field(default=None, ge=1)
    image_max_count: int | None = Field(default=None, ge=1)
    notes: list[str] = Field(default_factory=list)


class StickerPostPayload(BaseModel):
    title: str
    body: str
    interaction_prompt: str = ""
    risk_disclaimer: str = Field(min_length=30)
    constraints: PlatformConstraintSnapshot
    stock_names: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_verified_limits(self):
        if self.constraints.title_max_chars is not None and len(self.title) > self.constraints.title_max_chars:
            raise ValueError("sticker title exceeds verified platform limit")
        if self.constraints.body_max_chars is not None and len(self.body) > self.constraints.body_max_chars:
            raise ValueError("sticker body exceeds verified platform limit")
        return self


class DraftPackage(BaseModel):
    finance_deep: ArticlePayload | None = None
    finance_broad: ArticlePayload | None = None
    wechat_sticker_post: StickerPostPayload | None = None


class VisualAsset(BaseModel):
    article_mode: Literal["FINANCE_DEEP", "FINANCE_BROAD", "WECHAT_STICKER_POST"]
    role: Literal["hero", "section", "sticker"]
    semantic_focus: str
    source_uri: str
    anchor_after_block: int | None = Field(default=None, ge=0)
    hook_text: str = ""
    aspect_ratio: str = "16:9"
    avatar_included: bool = True


class VisualPackage(BaseModel):
    assets: list[VisualAsset] = Field(min_length=1)
    avatar_required: bool = True
    target_chars_per_section_image: int = Field(default=700, ge=200, le=2000)
    planning_notes: list[str] = Field(default_factory=list)


class StyleAuditDecision(BaseModel):
    status: Literal["PASS", "REVISE"]
    evidence: list[str]
    detected_patterns: list[str] = Field(default_factory=list)
    transition_findings: list[str] = Field(default_factory=list)
    extreme_language_findings: list[str] = Field(default_factory=list)
    revision_notes: list[str] = Field(default_factory=list)


class GateDecision(BaseModel):
    status: Literal["PASS", "REVISE", "FAIL"]
    evidence: list[str]
    defects: list[str] = Field(default_factory=list)
    revision_target: Literal["RESEARCH", "EDITORIAL", "TITLE", "DRAFT", "DELIVERY"] | None = None
    remaining_boundaries: list[str] = Field(default_factory=list)
