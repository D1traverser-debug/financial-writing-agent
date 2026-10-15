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


CausalConfidence = Literal[
    "VERIFIED_FACT",
    "SUPPORTED_MECHANISM",
    "PLAUSIBLE_INTERPRETATION",
    "UNRESOLVED",
]

MarketExplanationScope = Literal["REQUIRED", "NOT_MATERIAL"]
CompanyMateriality = Literal["MATERIAL", "SECONDARY", "REFERENCE_ONLY"]
UniverseCoverageStatus = Literal["COMPLETE", "BOUNDED_WITH_GAPS", "NOT_APPLICABLE"]
ValueChainCoverageStatus = Literal["COMPLETE", "BOUNDED_WITH_GAPS", "NOT_APPLICABLE"]
AuditAssurance = Literal["INDEPENDENT_EXECUTOR", "CHAT_SELF_REVIEW"]
HeadlineAngleFamily = Literal[
    "hard_fact",
    "profit_orders",
    "supply_demand",
    "company_divergence",
    "policy_transmission",
    "expectation_gap",
    "valuation_capital",
    "global_comparison",
    "validation_risk",
    "market_selection",
    "other",
]


class AuditProvenance(StrictModel):
    assurance: AuditAssurance = "CHAT_SELF_REVIEW"
    reviewer_identity: str = "chat-self"
    author_identity: str = "unknown"
    execution_ref: str = ""

    @model_validator(mode="after")
    def validate_independence(self):
        if self.assurance == "INDEPENDENT_EXECUTOR":
            if not self.execution_ref:
                raise ValueError("independent audit requires execution_ref")
            if self.reviewer_identity == self.author_identity:
                raise ValueError("independent audit reviewer_identity must differ from author_identity")
        return self


class MarketExplanationHypothesis(StrictModel):
    mechanism: str = Field(min_length=1)
    confidence: CausalConfidence
    applies_to: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    counterevidence: list[str] = Field(default_factory=list)
    time_horizon: str = ""

    @model_validator(mode="after")
    def evidence_matches_confidence(self):
        if self.confidence != "UNRESOLVED" and not self.evidence_refs:
            raise ValueError("non-UNRESOLVED market explanation requires evidence_refs")
        return self


class CompanyFinding(StrictModel):
    name: str = Field(min_length=1)
    ticker: str | None = None
    value_chain_class: str = Field(min_length=1)
    materiality: CompanyMateriality = "MATERIAL"
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
    exposure_type: Literal[
        "DIRECT_EARNINGS",
        "DIRECT_BUSINESS",
        "ECONOMIC_LINK",
        "SECOND_ORDER",
        "OPTIONALITY",
        "NARRATIVE_ONLY",
        "UNCLEAR",
    ] = "UNCLEAR"
    benefit_path: list[str] = Field(default_factory=list)
    sensitivity_basis: list[str] = Field(default_factory=list)
    realization_horizon: str = ""
    market_selection_signals: list[str] = Field(default_factory=list)
    continuation_support: list[str] = Field(default_factory=list)
    reversal_risks: list[str] = Field(default_factory=list)


class CompanyDecisionDimension(StrictModel):
    dimension: str = Field(min_length=1)
    company_assessments: dict[str, str] = Field(min_length=2)
    evidence_refs: list[str] = Field(min_length=1)
    why_it_changes_judgment: str = Field(min_length=1)


class CompanyDecisionMap(StrictModel):
    """Evidence-bounded company differentiation, not an actionable recommendation ranking."""

    material_companies: list[str] = Field(min_length=2)
    dimensions: list[CompanyDecisionDimension] = Field(min_length=2)
    current_comparative_verdict: str = Field(min_length=1)
    strongest_current_evidence_for: list[str] = Field(min_length=1)
    weaker_or_later_evidence_for: list[str] = Field(default_factory=list)
    change_conditions: list[str] = Field(min_length=1)
    non_actionable_boundary: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_company_accounting(self):
        names = set(self.material_companies)
        for dimension in self.dimensions:
            if set(dimension.company_assessments) != names:
                raise ValueError("each company-decision dimension must assess every material company")
        return self


class UniverseExclusion(StrictModel):
    name: str = Field(min_length=1)
    value_chain_class: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)


class UniverseClassCoverage(StrictModel):
    class_name: str = Field(min_length=1)
    economic_role: str = Field(min_length=1)
    included_companies: list[str] = Field(default_factory=list)
    excluded_companies: list[str] = Field(default_factory=list)
    unresolved_candidates: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def class_has_accounting(self):
        if not (self.included_companies or self.excluded_companies or self.unresolved_candidates):
            raise ValueError("each material value-chain class needs included, excluded, or unresolved company accounting")
        return self


class UniverseCoverage(StrictModel):
    status: UniverseCoverageStatus
    classes: list[UniverseClassCoverage] = Field(default_factory=list)
    recall_sources: list[str] = Field(default_factory=list)
    exclusions: list[UniverseExclusion] = Field(default_factory=list)
    missing_classes: list[str] = Field(default_factory=list)
    stop_reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_status(self):
        if self.status == "NOT_APPLICABLE":
            if self.classes or self.recall_sources or self.missing_classes:
                raise ValueError("NOT_APPLICABLE universe coverage cannot carry company-class coverage")
            return self
        if not self.classes:
            raise ValueError("company/theme research requires material value-chain classes")
        if len(self.recall_sources) < 2:
            raise ValueError("company/theme universe recall requires at least two materially different recall sources")
        if self.status == "COMPLETE" and self.missing_classes:
            raise ValueError("COMPLETE universe coverage cannot declare missing_classes")
        if self.status == "BOUNDED_WITH_GAPS" and not self.missing_classes:
            raise ValueError("BOUNDED_WITH_GAPS must declare missing_classes")
        return self


class ValueChainClassCoverage(StrictModel):
    class_name: str = Field(min_length=1)
    economic_role: str = Field(min_length=1)
    relationships: list[str] = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)


class ValueChainCoverageMap(StrictModel):
    status: ValueChainCoverageStatus
    classes: list[ValueChainClassCoverage] = Field(default_factory=list)
    transmission_paths: list[str] = Field(default_factory=list)
    excluded_or_unresolved_classes: list[str] = Field(default_factory=list)
    recall_sources: list[str] = Field(default_factory=list)
    sufficiency_reason: str = Field(min_length=1)
    thesis_selection_started_after_preflight: bool
    late_material_class_found: bool = False
    thesis_retested_after_late_discovery: bool = False

    @model_validator(mode="after")
    def validate_preflight(self):
        if not self.thesis_selection_started_after_preflight:
            raise ValueError("thesis selection may start only after value-chain preflight")
        if self.late_material_class_found and not self.thesis_retested_after_late_discovery:
            raise ValueError("late material value-chain discovery requires thesis re-test")
        if self.status == "NOT_APPLICABLE":
            if self.classes or self.transmission_paths or self.recall_sources or self.excluded_or_unresolved_classes:
                raise ValueError("NOT_APPLICABLE value-chain coverage cannot carry chain-map evidence")
            return self
        if not self.classes:
            raise ValueError("value-chain preflight requires material chain classes")
        if not self.transmission_paths:
            raise ValueError("value-chain preflight requires economic transmission paths")
        if len(self.recall_sources) < 2:
            raise ValueError("value-chain preflight requires at least two materially different recall/evidence sources")
        if self.status == "COMPLETE" and self.excluded_or_unresolved_classes:
            raise ValueError("COMPLETE value-chain coverage cannot declare unresolved classes")
        if self.status == "BOUNDED_WITH_GAPS" and not self.excluded_or_unresolved_classes:
            raise ValueError("BOUNDED_WITH_GAPS value-chain coverage must declare unresolved/excluded classes")
        return self


class MarketExplanationMap(StrictModel):
    activation_reason: str = Field(min_length=1)
    concept_subtheme_map: list[str] = Field(min_length=1)
    economic_benefit_dimensions: list[str] = Field(min_length=1)
    cross_sectional_selection_dimensions: list[str] = Field(min_length=1)
    hypotheses_considered: list[MarketExplanationHypothesis] = Field(min_length=2)
    why_not_evidence: list[str] = Field(min_length=1)
    continuation_conditions: list[str] = Field(min_length=1)
    reversal_conditions: list[str] = Field(min_length=1)
    unresolved_questions: list[str] = Field(default_factory=list)


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
    value_chain_coverage: ValueChainCoverageMap
    universe: list[CompanyFinding] = Field(default_factory=list)
    universe_coverage: UniverseCoverage
    company_decision_map: CompanyDecisionMap | None = None
    market_explanation_scope: MarketExplanationScope
    market_explanation_scope_reason: str = Field(min_length=1)
    market_explanation: MarketExplanationMap | None = None
    evidence_ledger: list[EvidenceItem] = Field(min_length=1)
    counterevidence: list[str] = Field(default_factory=list)
    unresolved_gaps: list[str] = Field(default_factory=list)
    provisional_theses: list[str] = Field(min_length=1)
    source_boundary: str = Field(min_length=1)
    cognition: MarketCognition
    coverage: ResearchCoverage
    knowledge_writeback_candidates: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_research_contract(self):
        if self.market_explanation_scope == "REQUIRED" and self.market_explanation is None:
            raise ValueError("market_explanation_scope=REQUIRED requires market_explanation")
        if self.market_explanation_scope == "NOT_MATERIAL" and self.market_explanation is not None:
            raise ValueError("market_explanation_scope=NOT_MATERIAL must not include market_explanation")

        names = [company.name for company in self.universe]
        if len(names) != len(set(names)):
            raise ValueError("research universe company names must be unique")
        if self.universe:
            if self.universe_coverage.status == "NOT_APPLICABLE":
                raise ValueError("non-empty company universe requires COMPLETE or BOUNDED_WITH_GAPS universe_coverage")
            class_names = {item.class_name for item in self.universe_coverage.classes}
            if any(company.value_chain_class not in class_names for company in self.universe):
                raise ValueError("every universe company must map to a declared material value-chain class")
            ledger_names = {name for item in self.universe_coverage.classes for name in item.included_companies}
            missing_from_ledger = set(names) - ledger_names
            if missing_from_ledger:
                raise ValueError(f"universe companies missing from class coverage ledger: {sorted(missing_from_ledger)}")
        elif self.universe_coverage.status != "NOT_APPLICABLE":
            accounted = any(item.included_companies for item in self.universe_coverage.classes)
            if accounted:
                raise ValueError("universe_coverage included_companies require matching universe entries")

        material = [company.name for company in self.universe if company.materiality == "MATERIAL"]
        # Historical stored packages remain parseable when this new optional field is absent;
        # current Research/Audit admission applies the hard rule through policy/checks. When a
        # map is supplied, its company set must be exact.
        if self.company_decision_map is not None and set(self.company_decision_map.material_companies) != set(material):
            raise ValueError("company_decision_map.material_companies must exactly match current MATERIAL companies")
        return self


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
    company_coverage_obligations: list[str] = Field(default_factory=list)
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
    angle_family: HeadlineAngleFamily
    target_reader: str = Field(min_length=1)
    finance_relevance: str = Field(min_length=1)
    target_reader_click_reason: str = Field(min_length=1)
    broader_finance_relevance: str = ""
    primary_gap: str = Field(min_length=1)
    promised_payoff: str = Field(min_length=1)
    headline_form: Literal["statement", "question", "other"] = "statement"
    cognitive_load: Literal["low", "medium", "high"]
    wechat_search_terms: list[str] = Field(min_length=1)
    search_evidence_refs: list[str] = Field(min_length=1)


class HeadlinePackage(StrictModel):
    finance_deep_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    finance_broad_candidates: list[HeadlineCandidate] = Field(default_factory=list)
    finance_deep_selected: str | None = None
    finance_broad_selected: str | None = None

    @model_validator(mode="after")
    def candidate_sets_are_diverse(self):
        for selected, candidates, label in [
            (self.finance_deep_selected, self.finance_deep_candidates, "finance_deep"),
            (self.finance_broad_selected, self.finance_broad_candidates, "finance_broad"),
        ]:
            if not candidates:
                if selected is not None:
                    raise ValueError(f"{label}_selected cannot exist without candidates")
                continue
            if not 8 <= len(candidates) <= 12:
                raise ValueError(f"{label}_candidates must contain 8-12 candidates")
            titles = [candidate.title for candidate in candidates]
            if len(titles) != len(set(titles)):
                raise ValueError(f"{label}_candidates must contain unique titles")
            families = {candidate.angle_family for candidate in candidates}
            if len(families) < 5:
                raise ValueError(f"{label}_candidates need at least 5 distinct angle families; synonym/title-mold swaps are not enough")
            if selected and selected not in set(titles):
                raise ValueError(f"{label}_selected must be one of its candidates")
        return self


class ArticleBlock(StrictModel):
    kind: Literal["lead", "h1", "h2", "h3", "body"]
    text: str = Field(min_length=1)


class ArticlePayload(StrictModel):
    title: str = Field(min_length=1)
    blocks: list[ArticleBlock] = Field(min_length=3)
    risk_disclaimer: str = Field(min_length=1)
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


class InteractionPost(StrictModel):
    platform_family: Literal["WECHAT_IMAGE_TEXT", "TOUTIAO_MICRO", "BAIJIAHAO_DYNAMIC", "NETEASE_DYNAMIC", "GENERIC_DYNAMIC"]
    hook: str = Field(min_length=1)
    body: str = Field(min_length=1)
    interaction_prompt: str = Field(min_length=1)
    stock_names: list[str] = Field(default_factory=list)


class PlatformInteractionPack(StrictModel):
    topic: str = Field(min_length=1)
    posts: list[InteractionPost] = Field(min_length=3)
    evidence_boundary: str = Field(min_length=1)
    independent_rewrite_from_long_form: bool = True

    @model_validator(mode="after")
    def ensure_independent_rewrite(self):
        if not self.independent_rewrite_from_long_form:
            raise ValueError("platform interaction pack must be independently rewritten from the audited evidence base")
        families = {post.platform_family for post in self.posts}
        if len(families) < 3:
            raise ValueError("platform interaction pack requires at least three platform-family adaptations")
        return self


class DraftPackage(StrictModel):
    finance_deep: ArticlePayload | None = None
    finance_broad: ArticlePayload | None = None
    platform_interaction_pack: PlatformInteractionPack | None = None


class AuthorialProseAuditRubric(StrictModel):
    fidelity_and_responsibility: Literal["PASS", "REVISE"]
    semantic_contribution: Literal["PASS", "REVISE"]
    argument_progression: Literal["PASS", "REVISE"]
    reader_calibration: Literal["PASS", "REVISE"]
    authorial_selectivity: Literal["PASS", "REVISE"]
    evidence_specificity: Literal["PASS", "REVISE"]
    structural_rhythm_naturalness: Literal["PASS", "REVISE"]
    template_redundancy_control: Literal["PASS", "REVISE"]
    uncertainty_rhetoric_calibration: Literal["PASS", "REVISE"]


class StyleAuditDecision(StrictModel):
    status: Literal["PASS", "REVISE"]
    evidence: list[str] = Field(min_length=1)
    rubric: AuthorialProseAuditRubric
    provenance: AuditProvenance = Field(default_factory=AuditProvenance)
    detected_patterns: list[str] = Field(default_factory=list)
    reasoning_findings: list[str] = Field(default_factory=list)
    revision_target: Literal["DRAFT"] | None = None
    revision_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_matches_rubric(self):
        expected = "PASS" if all(value == "PASS" for value in self.rubric.model_dump().values()) else "REVISE"
        if self.status != expected:
            raise ValueError(f"authorial-prose status must be {expected} for the supplied rubric")
        if self.status == "REVISE" and (not self.revision_notes or self.revision_target != "DRAFT"):
            raise ValueError("REVISE authorial-prose audit requires revision_target=DRAFT and revision_notes")
        if self.status == "PASS" and self.revision_target is not None:
            raise ValueError("PASS authorial-prose audit must not set revision_target")
        return self


class HookAuditRubric(StrictModel):
    audience_promise_fit: Literal["PASS", "REVISE"]
    headline_information_value: Literal["PASS", "REVISE"]
    headline_curiosity_balance: Literal["PASS", "REVISE"]
    headline_strategy_diversity: Literal["PASS", "REVISE"]
    title_wechat_search_intent: Literal["PASS", "REVISE"]
    # Compatibility field name retained. Current semantics are now a hard three-sentence
    # opening-zone job test: the first three complete sentences collectively establish a
    # hard fact/anomaly, finance-wide consequence, and a material unresolved payoff. The
    # order and syntax remain flexible, and the full title answer need not be exhausted.
    opening_three_sentence_retention: Literal["PASS", "REVISE"]
    continuation_flow: Literal["PASS", "REVISE"]
    completion_payoff: Literal["PASS", "REVISE"]
    title_opening_payoff: Literal["PASS", "REVISE"]


class HookAuditDecision(StrictModel):
    status: Literal["PASS", "REVISE"]
    evidence: list[str] = Field(min_length=1)
    rubric: HookAuditRubric
    provenance: AuditProvenance = Field(default_factory=AuditProvenance)
    search_terms_checked: list[str] = Field(min_length=1)
    search_evidence_refs: list[str] = Field(min_length=1)
    revision_target: Literal["TITLE", "DRAFT"] | None = None
    revision_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_matches_rubric(self):
        expected = "PASS" if all(value == "PASS" for value in self.rubric.model_dump().values()) else "REVISE"
        if self.status != expected:
            raise ValueError(f"reader-funnel hook status must be {expected} for the supplied rubric")
        if self.status == "REVISE" and (not self.revision_notes or self.revision_target is None):
            raise ValueError("REVISE reader-funnel hook audit requires revision_target and revision_notes")
        if self.status == "PASS" and self.revision_target is not None:
            raise ValueError("PASS reader-funnel hook audit must not set revision_target")
        return self


class GateDecision(StrictModel):
    status: Literal["PASS", "REVISE", "FAIL"]
    evidence: list[str] = Field(min_length=1)
    provenance: AuditProvenance = Field(default_factory=AuditProvenance)
    defects: list[str] = Field(default_factory=list)
    revision_target: Literal["RESEARCH", "EDITORIAL", "TITLE", "DRAFT", "DELIVERY"] | None = None
    remaining_boundaries: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def decision_is_actionable(self):
        if self.status in {"REVISE", "FAIL"} and self.revision_target is None:
            raise ValueError(f"{self.status} requires revision_target")
        if self.status == "FAIL" and not self.defects:
            raise ValueError("FAIL requires at least one defect")
        if self.status == "PASS" and self.revision_target is not None:
            raise ValueError("PASS must not set revision_target")
        return self
