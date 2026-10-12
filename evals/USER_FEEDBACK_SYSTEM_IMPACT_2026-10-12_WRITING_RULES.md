# User Feedback System Impact — Writing Rule Calibration — 2026-10-12

Status: DESIGN_REVIEWED__IMPLEMENTATION_PENDING
Scope: owner-local Financial Writing business rules, delivery mechanics, audit completeness, Reader Funnel evolution
Trigger task: fw-20261012-ai-security-6dd14859

## M0 — Signal classification

The user supplied explicit durable corrections after reviewing the current Financial Writing requirement summary.

### Goal / constraint
- Rules must remain cross-topic and must not accidentally promote an article-specific example (AI security) into a domain-general writing rule.
- Deep articles should use visible lower-level hierarchy more often when it materially improves reading/navigation.
- Title promises must be honored, but immediate opening payoff is not universally mandatory.
- Opening/reader-funnel methods should continue to learn and evolve rather than freeze into a single first-three-sentence formula.
- All A-share company names in publication prose should be bold.
- Additional selected facts/judgment sentences must still be bold so title + H1 + bold spans reconstruct the article's main line.
- Company comparison may be prominent and may identify stronger/weaker evidence or operating realization, while remaining non-actionable.
- The final risk paragraph may be shorter when information completeness is preserved; length is not itself quality.
- Audit should cover the complete applicable writing contract by default, except requirements that are genuinely stage/mode/surface-specific.

### Failure / counterexample
- A prior requirement summary rendered a topic-specific example as a general rule: “有AI产品不能等同于AI已经贡献利润”. The underlying invariant is evidence-stage non-escalation, not AI-specific.
- Current policy hard-codes title_opening_payoff_required=true, auto_bold_company_names=false and risk min_body_chars=60, conflicting with the user's durable requirements.
- Existing audit documentation says company names need not all be bold, also conflicting with the user's durable requirement.

### Proposed mechanisms from user
- Use more numbered hierarchy.
- Make all A-share company names bold.
- Continue learning Reader Funnel/opening methods, optionally via Universal evolution.
- Keep risk wording concise without reducing information.

These mechanisms are treated as candidates where implementation details remain open; the user-owned requirements themselves are authoritative.

## M1/M2 — Root cause and impact map

Root cause is split across:
- TRANSCRIPTION: assistant summarized a generic evidence-stage rule with an AI-specific example as if it were canonical.
- REPOSITORY_POLICY: title-opening timing, risk length and company-bold mechanics conflict with the user's current durable instruction.
- RUNTIME/DELIVERY: Word builder currently preserves only explicit **...** spans and intentionally does not auto-bold stock names.
- AUDIT: audit currently explicitly rejects a blanket company-bold requirement and Reader Funnel treats title/opening payoff as a hard check.

Affected authority/runtime surfaces:
- references/editorial.md
- references/hooks.md
- references/style.md
- references/delivery.md
- references/audit.md
- config/policy.json plus packaged mirror
- financial_writing_agent/document.py
- financial_writing_agent/checks.py
- tests/test_document.py
- intentional mirrors of canonical references/policy

No stage graph, business-state schema or public MCP contract change is required.

## M3 — Learning / evidence scout

Universal operational_hygiene@1.0 + evolution@1.0 was consulted through continuity/UNIVERSAL_PROTOCOL_ADAPTER.json.

External benchmark findings were used only for Reader Funnel method design:
- Information-foraging / information-scent research supports early clarity that the page is relevant and likely to answer the reader's need, but does not require that the entire headline answer appear in sentence one.
- Journalism practice supports both direct summary leads and delayed/feature leads. Nut-graf structures can begin with a scene/anecdote/question and then provide the article's significance and promise early enough to preserve reader orientation.

Disposition: ADOPT the principle of multiple legal opening strategies with early relevance/orientation and eventual promise fulfillment. REJECT a single mandatory immediate-payoff or fixed three-sentence template.

## M4 — Alternatives and falsification

### Alternative A — Keep current hard immediate-payoff rule
Pros: easy to audit; strong anti-clickbait guard.
Failure mode: forces repetitive inverted-pyramid openings and suppresses legitimate analytical/delayed leads. Rejected.

### Alternative B — Remove title/opening relationship rule entirely
Pros: maximum stylistic freedom.
Failure mode: permits bait-and-switch and weak information scent. Rejected.

### Alternative C — Promise integrity + strategy-specific payoff timing
Require title/body fidelity, early reader orientation/information scent and a clear payoff zone appropriate to the chosen lead strategy; immediate payoff remains valid but not mandatory. Accepted.

For A-share bolding:
- manual explicit bold only is too easy to omit and conflicts with the user's formatting requirement;
- automatic builder bolding from ArticleDocument.stock_names is deterministic and preserves additional explicit skim anchors. Accepted.

For risk length:
- fixed minimum character count is a weak proxy and can force boilerplate;
- semantic completeness plus exactly-one/italic/topic-specific mechanical requirements is preferable. Accepted.

## M5/M6 — Control surface and complexity decision

No account/startup instruction change is required. Existing owner-local authorities can own all changes.

Net complexity effect:
- no new root policy or agent;
- one small deterministic builder behavior change;
- simplified risk check by removing the fixed minimum-length gate;
- Reader Funnel rule becomes less rigid but remains auditable through strategy declaration and evidence;
- audit coverage becomes more systematic by deriving default checks from the applicable writing contract instead of a hand-curated subset.

## M7 — Intended implementation

1. Generalize evidence-stage non-escalation language; never encode AI-specific terminology as a cross-topic invariant.
2. Strengthen lower-level numbered navigation preference for genuinely branched FINANCE_DEEP reasoning.
3. Replace hard title-opening-immediate-payoff with promise integrity + strategy-specific payoff timing.
4. Add opening-strategy diversity guidance (direct fact, contradiction, delayed/nut-graf, question, scene/example when evidence-supported) without forcing one formula.
5. Auto-bold every A-share stock/company name supplied in ArticleDocument.stock_names while preserving explicit **...** skim anchors.
6. Keep/select additional bold facts/numbers/judgment sentences so the skim path remains reconstructive.
7. State that evidence-bounded company comparison may be a major analytical focus, while actionable trading instructions remain prohibited.
8. Remove fixed 60-character risk minimum; audit for concise completeness instead.
9. Make audit completeness default to all applicable writing requirements, with explicit N/A/special-surface exceptions rather than silent omission.
10. Update deterministic tests and intentional mirrors.

## M8/M10 — Validation / second-order challenge

Required regression evidence:
- all occurrences of A-share stock names become bold even without explicit ** markers;
- explicit skim anchors remain bold;
- overseas/non-stock entities are not accidentally auto-bolded unless explicitly emphasized;
- concise but substantive risk paragraph passes; missing/duplicate/non-italic risk still fails;
- policy no longer declares immediate title-opening payoff as a hard requirement;
- references and packaged mirrors remain synchronized;
- current document typography/no-table/no-underline checks remain intact.

Second-order risks:
- blanket A-share bolding can over-emphasize company-dense paragraphs; accepted because this is an explicit user formatting preference, while additional semantic anchors still carry the argument signal.
- relaxing immediate payoff can regress into vague openings; mitigate by requiring early information scent / reader orientation and prohibiting bait-and-switch or excessively delayed promise fulfillment.
- removing a risk character floor can yield token disclaimers; semantic audit must check topic-specific coverage rather than length.

Assurance ceiling: repository/rule/runtime changes can be regression-verified, but live writing-quality improvement remains OPEN until exercised on later article trajectories and user feedback.
