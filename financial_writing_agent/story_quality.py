from __future__ import annotations

import re
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProductMode(str, Enum):
    FINANCE_DEEP = "FINANCE_DEEP"
    FINANCE_BROAD = "FINANCE_BROAD"


class NarrativeEngine(str, Enum):
    HARD_ANOMALY = "HARD_ANOMALY"
    COMPANY_CONFLICT = "COMPANY_CONFLICT"
    REVERSAL = "REVERSAL"
    MYSTERY = "MYSTERY"
    SYSTEM_MAP = "SYSTEM_MAP"
    CONSEQUENCE_CHAIN = "CONSEQUENCE_CHAIN"
    CHARACTER_OR_CASE = "CHARACTER_OR_CASE"
    TIMELINE_ESCALATION = "TIMELINE_ESCALATION"


class AuditStatus(str, Enum):
    PASS = "PASS"
    REVISE = "REVISE"


class OpeningDesign(StrictModel):
    concrete_anchor: str = Field(min_length=1)
    hard_fact_or_scene: str = Field(min_length=1)
    reader_information_gap: str = Field(min_length=1)
    why_reader_should_care: str = Field(min_length=1)
    early_payoff: str = Field(min_length=1)
    deliberately_withheld_payoff: str = Field(min_length=1)

    @model_validator(mode="after")
    def no_empty_clickbait_gap(self):
        if self.deliberately_withheld_payoff == self.early_payoff:
            raise ValueError("opening must preserve a real unresolved payoff after its early payoff")
        return self


class SectionBlueprint(StrictModel):
    sequence_label: str = Field(min_length=1)
    working_heading: str = Field(min_length=1)
    reader_question: str = Field(min_length=1)
    new_information: list[str] = Field(min_length=1)
    company_anchors: list[str] = Field(default_factory=list)
    value_chain_classes: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(min_length=1)
    tension_or_open_loop: str = Field(min_length=1)
    section_payoff: str = Field(min_length=1)
    bridge_to_next: str = Field(min_length=1)
    is_material_explanatory_section: bool = True

    @model_validator(mode="after")
    def material_sections_need_company_grounding(self):
        if self.is_material_explanatory_section and not self.company_anchors:
            raise ValueError("material explanatory section must ground the mechanism in named company/case anchors")
        return self


class StoryBlueprint(StrictModel):
    product_mode: ProductMode
    reader_job: str = Field(min_length=1)
    reader_starting_state: str = Field(min_length=1)
    article_promise: str = Field(min_length=1)
    central_question: str = Field(min_length=1)
    author_stance: str = Field(min_length=1)
    narrative_engine: NarrativeEngine
    opening: OpeningDesign
    sections: list[SectionBlueprint] = Field(min_length=3)
    material_value_chain_classes: list[str] = Field(default_factory=list)
    default_word_limit: int | None = None
    ending_payoff: str = Field(min_length=1)
    voice_evidence_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_story_architecture(self):
        expected_prefixes = [
            "一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、",
            "十一、", "十二、", "十三、", "十四、", "十五、",
        ]
        labels = [section.sequence_label for section in self.sections]
        if len(labels) != len(set(labels)):
            raise ValueError("section sequence labels must be unique")
        for idx, label in enumerate(labels):
            if idx >= len(expected_prefixes) or label != expected_prefixes[idx]:
                raise ValueError("H1 section sequence must be explicit and contiguous Chinese numbering")

        if self.product_mode == ProductMode.FINANCE_DEEP:
            if self.default_word_limit is not None:
                raise ValueError("FINANCE_DEEP has no default word-count ceiling; compress only by explicit user/product need")
            required = set(self.material_value_chain_classes)
            covered = {item for section in self.sections for item in section.value_chain_classes}
            missing = required - covered
            if missing:
                raise ValueError(f"FINANCE_DEEP blueprint omits material value-chain classes: {sorted(missing)}")
        return self


class TextEvidence(StrictModel):
    location: str = Field(min_length=1)
    excerpt: str = Field(min_length=1)
    finding: str = Field(min_length=1)
    severity: Literal["INFO", "MINOR", "MAJOR", "CRITICAL"]


class GateAudit(StrictModel):
    gate: Literal[
        "FACT_INTEGRITY",
        "RETENTION",
        "COMPANY_GROUNDING",
        "STRUCTURE_NUMBERING",
        "ORIGINALITY",
        "AUTHORIAL_STYLE",
        "COMPLIANCE",
        "PAYOFF",
    ]
    status: AuditStatus
    evidence: list[TextEvidence] = Field(min_length=1)
    checked_items: list[str] = Field(min_length=1)
    revision_actions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_matches_findings(self):
        serious = any(item.severity in {"MAJOR", "CRITICAL"} for item in self.evidence)
        if serious and self.status == AuditStatus.PASS:
            raise ValueError("gate with MAJOR/CRITICAL finding cannot PASS")
        if self.status == AuditStatus.REVISE and not self.revision_actions:
            raise ValueError("REVISE gate requires concrete revision actions")
        return self


class OriginalityEvidence(StrictModel):
    compared_source_ref: str = Field(min_length=1)
    checked_phrase_or_passage: str = Field(min_length=1)
    result: Literal["NO_MATERIAL_OVERLAP", "COMMON_LANGUAGE", "NEEDS_REWRITE"]
    notes: str = Field(min_length=1)


class PublicationFitness(StrictModel):
    product_mode: ProductMode
    gates: list[GateAudit] = Field(min_length=8)
    originality_checks: list[OriginalityEvidence] = Field(min_length=1)
    deterministic_findings: list[str] = Field(default_factory=list)
    assurance: Literal["CHAT_SELF_REVIEW", "INDEPENDENT_EXECUTOR"]
    final_status: AuditStatus

    @model_validator(mode="after")
    def require_all_named_gates(self):
        required = {
            "FACT_INTEGRITY",
            "RETENTION",
            "COMPANY_GROUNDING",
            "STRUCTURE_NUMBERING",
            "ORIGINALITY",
            "AUTHORIAL_STYLE",
            "COMPLIANCE",
            "PAYOFF",
        }
        names = [gate.gate for gate in self.gates]
        if set(names) != required or len(names) != len(required):
            raise ValueError("publication fitness requires exactly one audit for every mandatory gate")
        expected = AuditStatus.PASS if all(g.status == AuditStatus.PASS for g in self.gates) else AuditStatus.REVISE
        if self.final_status != expected:
            raise ValueError(f"final_status must be {expected.value} for supplied gate decisions")
        if any(item.result == "NEEDS_REWRITE" for item in self.originality_checks) and self.final_status == AuditStatus.PASS:
            raise ValueError("originality overlap requiring rewrite blocks publication PASS")
        return self


_GENERIC_THROAT_CLEARING = [
    re.compile(pattern)
    for pattern in (
        r"值得(?:关注|注意|一提|观察)",
        r"需要(?:关注|注意|看到|指出)",
        r"从这个角度(?:看|来看)",
        r"可以(?:看到|发现|看出)",
        r"不难发现",
        r"这(?:也)?说明",
        r"这意味着",
        r"问题在于",
        r"真正(?:值得|需要|的变化)",
        r"换句话说",
    )
]


def publication_structure_findings(headings: list[str]) -> list[str]:
    """Deterministic structural tripwire; semantic quality remains evidence-based."""
    findings: list[str] = []
    expected = ["一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、"]
    for idx, heading in enumerate(headings):
        if idx >= len(expected) or not heading.startswith(expected[idx]):
            findings.append(f"non-contiguous-or-missing-H1-sequence:{idx}:{heading}")
    return findings


def generic_scaffolding_findings(text: str) -> dict[str, int | float | bool]:
    hits = sum(len(pattern.findall(text)) for pattern in _GENERIC_THROAT_CLEARING)
    density = round(hits * 1000 / max(len(text), 1), 2)
    return {
        "hits": hits,
        "density_per_1000_chars": density,
        "requires_semantic_style_review": hits >= 4 and density >= 1.0,
    }
