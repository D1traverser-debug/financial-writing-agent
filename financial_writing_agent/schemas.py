from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


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


class HeadlineCandidate(BaseModel):
    title: str
    angle: str
    finance_relevance: str
    primary_gap: str
    cognitive_load: Literal["low", "medium", "high"]


class HeadlinePackage(BaseModel):
    finance_deep_candidates: list[HeadlineCandidate]
    finance_broad_candidates: list[HeadlineCandidate]
    finance_deep_selected: str | None = None
    finance_broad_selected: str | None = None


class ArticleBlock(BaseModel):
    kind: Literal["lead", "h1", "h2", "h3", "body"]
    text: str


class ArticlePayload(BaseModel):
    title: str
    blocks: list[ArticleBlock]
    stock_names: list[str] = Field(default_factory=list)


class DraftPackage(BaseModel):
    finance_deep: ArticlePayload | None = None
    finance_broad: ArticlePayload | None = None


class GateDecision(BaseModel):
    status: Literal["PASS", "REVISE", "FAIL"]
    evidence: list[str]
    defects: list[str] = Field(default_factory=list)
    revision_target: Literal["RESEARCH", "EDITORIAL", "TITLE", "DRAFT", "DELIVERY"] | None = None
    remaining_boundaries: list[str] = Field(default_factory=list)
