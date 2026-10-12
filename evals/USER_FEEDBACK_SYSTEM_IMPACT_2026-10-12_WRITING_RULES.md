# User Feedback System Impact — Writing Rule Calibration — 2026-10-12

Status: IMPLEMENTED__TARGETED_VALIDATION_PASS__HOSTED_CI_INFRA_OPEN
Scope: owner-local Financial Writing business rules, delivery mechanics, audit completeness, Reader Funnel evolution
Trigger task: fw-20261012-ai-security-6dd14859
Implementation PR: #18

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
- Current policy hard-coded title_opening_payoff_required=true, auto_bold_company_names=false and risk min_body_chars=60, conflicting with the user's durable requirements.
- Existing audit documentation said company names need not all be bold, also conflicting with the user's durable requirement.

### Proposed mechanisms from user
- Use more numbered hierarchy.
- Make all A-share company names bold.
- Continue learning Reader Funnel/opening methods, optionally via Universal evolution.
- Keep risk wording concise without reducing information.

These mechanisms were treated as candidates where implementation details remained open; the user-owned requirements themselves were authoritative.

## M1/M2 — Root cause and impact map

Root cause was split across:
- TRANSCRIPTION: assistant summarized a generic evidence-stage rule with an AI-specific example as if it were canonical.
- REPOSITORY_POLICY: title-opening timing, risk length and company-bold mechanics conflicted with the user's current durable instruction.
- RUNTIME/DELIVERY: Word builder preserved only explicit **...** spans and intentionally did not auto-bold stock names.
- SCHEMA: `ArticlePayload.risk_disclaimer` retained a hidden 60-character minimum even after policy-level relaxation would otherwise have been possible.
- AUDIT: audit explicitly rejected blanket company-bold requirement and Reader Funnel treated title/opening payoff as a hard check.

Affected authority/runtime surfaces:
- references/research.md
- references/editorial.md
- references/hooks.md
- references/style.md
- references/delivery.md
- references/audit.md
- config/policy.json plus packaged mirror
- config/rule_ownership.json
- financial_writing_agent/document.py
- financial_writing_agent/checks.py
- financial_writing_agent/schemas.py
- tests/test_document.py
- tests/test_user_rule_calibration_20261012.py
- intentional mirrors of canonical references/policy

No stage graph, business-state schema or public MCP execution contract change was required. Existing HookAuditRubric field names were retained for compatibility while their authority semantics were narrowed by `references/hooks.md`.

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

No account/startup instruction change is required. Existing owner-local authorities own all changes.

Net complexity effect:
- no new root policy or agent;
- one small deterministic builder behavior change;
- one deterministic QA invariant for every supplied A-share name occurrence;
- simplified risk check by removing the fixed minimum-length gate from policy and schema;
- Reader Funnel rule becomes less rigid but remains auditable through strategy declaration/evidence;
- audit coverage becomes more systematic by deriving default checks from the applicable writing contract instead of a hand-curated subset.

## M7 — Implemented change set

1. Generalized evidence-stage non-escalation language; AI-specific terminology is no longer treated as a cross-topic invariant.
2. Strengthened lower-level numbered navigation preference for genuinely branched FINANCE_DEEP reasoning.
3. Replaced hard title-opening-immediate-payoff with promise integrity + strategy-specific payoff timing.
4. Added opening-strategy diversity guidance: direct fact, contradiction, delayed/nut-graf, question and scene/example where evidence-supported.
5. Auto-bold every A-share stock/company name supplied in `ArticleDocument.stock_names` while preserving explicit `**...**` skim anchors.
6. Kept additional bold facts/numbers/judgment sentences as an independent semantic skim-path obligation.
7. Made evidence-bounded company comparison eligible to become a major analytical focus while preserving the non-actionable boundary.
8. Removed fixed 60-character risk minimum from policy and `ArticlePayload` schema; semantic audit now owns concise completeness.
9. Made audit completeness default to all applicable writing requirements, with explicit N/A/special-surface exceptions rather than silent omission.
10. Updated deterministic tests, rule ownership and intentional reference/policy mirrors.

## M8 — Validation evidence

### Static authority / propagation
PASS for the scoped changed rule set.

For each changed canonical reference (`research.md`, `editorial.md`, `hooks.md`, `style.md`, `delivery.md`, `audit.md`), the canonical path, packaged-resource mirror and Skill mirror were re-read from the maintenance branch and share the same Git blob SHA. `config/policy.json` and the packaged policy mirror also share the same updated content blob.

### Current-session targeted executable regression
PASS for the mechanisms exercised in-session:
- multiple supplied A-share names are detected and marked bold at every exact occurrence;
- an unlisted overseas entity is not auto-bolded;
- explicit semantic `**...**` anchors remain bold independently of company-name emphasis;
- a concise 20-character non-empty risk paragraph validates under the new schema, proving the old 60-character floor is not active in the exercised contract;
- policy assertions for flexible opening strategy, optional immediate payoff, generous branching hierarchy, comparison focus, two-layer bolding and full applicable-audit coverage are encoded in dedicated repository regressions.

This is action-level/current-session targeted evidence, not a substitute for full hosted CI.

### Hosted GitHub Actions
OPEN — infrastructure execution did not reach workflow steps.

PR #18 triggered `financial-writing-agent-ci` run `38218047830`. The run started at 2026-10-12T07:29:41Z and ended at 07:29:44Z with failure. The single job reports zero steps, and the job-log blob is unavailable/404. Therefore there is no evidence that dependency install, pytest, static audit, render smoke or any other repository CI step actually executed. This result is classified as hosted-CI infrastructure/runner failure, not a code-test failure and not a CI PASS.

Full hosted CI remains OPEN and must not be represented as executed successfully.

## M10 — Second-order challenge / remaining risk

- Blanket A-share bolding can over-emphasize company-dense paragraphs. Accepted because it is an explicit durable user formatting requirement; semantic anchors remain separately required so the skim path still communicates reasoning rather than only entities.
- Relaxing immediate payoff can regress into vague openings. Mitigation: early information scent/reader orientation remains required, title-promise integrity remains required, and bait-and-switch or excessively delayed payoff still fails.
- Removing a risk character floor can yield token disclaimers. Mitigation: exactly-one/non-empty/italic is mechanical; topic-specific information completeness is semantic and included in full applicable-contract audit.
- Legacy HookAuditRubric field names remain for compatibility. Their old names could be misread by code readers, so `schemas.py` carries explicit compatibility comments and canonical semantics live in `references/hooks.md` / policy. A future contract-version change may rename them, but this maintenance does not introduce an unnecessary breaking schema migration.

## Assurance ceiling

Current evidence supports: owner-local rule/routing consistency, deterministic implementation of A-share-name bolding, removal of fixed risk-length gating, mirror propagation and targeted current-session regression.

Current evidence does **not** support: full hosted-CI PASS, owner-native provider-attested verification, or a claim that future live article quality is already improved. Live writing outcome remains OPEN until exercised on later article trajectories and user feedback.
