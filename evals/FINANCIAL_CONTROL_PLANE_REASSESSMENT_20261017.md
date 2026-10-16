# Financial Writing control-plane reassessment — 2026-10-17

Status: `DOMAIN_CANDIDATE__ARCHITECTURE_REASSESSMENT_ACTIVE`
Owner: `DOMAIN:financial_writing`
Parent governance basis: user explicitly authorized total-controller review/refactor after repeated post-rebuild failures; parent UAOS issue #63 already carries the upcall stream.

## Governing outcome

Make current Financial Writing tasks reliably satisfy admitted task requirements, quality evidence, product-mode boundaries and delivery contracts through one current-task mutation boundary, without requiring the user to repeatedly detect drift or request repair. Preserve historical provenance and compatibility without letting historical/weak paths mutate current-governed tasks.

## Direct evidence

- Baseline production before this candidate: `63354a8e05959f5fd364795cdde1624c96519934`; an accidental direct-main audit write was immediately reverted as `4c6865baeb8cad067133e419b3ddcaa424e81906` and is retained as additional mutation-path failure evidence.
- Issue #45 contains repeated post-rebuild failures P1-P18, including output-channel drift, owner-state/artifact drift, late requirement propagation failure, PRIVATE_RESEARCH/DEEP boundary collapse, meta-language leakage, weak event-to-company payoff, active-task migration debt, active/historical namespace collision, explanation-first repair sequencing and causal anchoring.
- `cross-border-ecommerce-20261016-v2/STATE.json` is still a current writing-kernel task without Task Requirement Authority v1.0, proving the promoted P10 repair did not migrate the live pre-fix task.
- `owner_guard.validate_state` validates current quality evidence but does not enforce current Task Requirement Authority bindings; current `owner_guard.advance_state` remains a public mutation path parallel to `current_admission.advance_state`.
- `owner_lifecycle` and `proactive_resolution` mutate state/receipts through owner_guard primitives and therefore do not share one enforced current-governance transaction boundary.
- PR #47 Codex review identified requirement-marker stripping/public owner-path bypasses; current main still exhibits the same structural split.
- PR #46 merged before Codex review completed; the later review found three P1 delivery-provenance/builder/private-research binding defects and one P2 stock-name normalization defect. Current delivery code still contains corresponding weak structures.
- Current `main` is not branch protected and CI is trigger-based rather than a non-bypassable merge gate.
- Architecture/product/evolution documents lag runtime: runtime PrivateResearchBrief is 1.1 while persistent architecture/product records still contain candidate/1.0-era descriptions.

## Professional-method comparison

- DDD aggregate-root guidance: mutations that must preserve one consistency boundary should enter through one aggregate root, not through multiple child/public mutation surfaces.
- SRE incident learning: repeated failures across releases should be grouped by systemic root-cause classes rather than patched incident-by-incident.
- IV&V principle: promotion evidence should include an evaluator independent of the implementation premise; green self-tests alone do not close known findings.

## Competing architecture candidates

### A — NO_CHANGE + migrate current article only
Disposition: `REJECTED`
Falsification: acceptable only if current runtime already has one non-divergent mutation boundary. Current code and PR findings show multiple paths with unequal invariants.

### B — patch each current guard independently
Disposition: `REJECTED_AS_PRIMARY_ARCHITECTURE`
Falsification: acceptable only if failures are isolated. The repeated history shows the same declaration-to-operation/bypass class reappearing across requirement, lifecycle, delivery and finalization surfaces.

### C — single current Article Aggregate mutation boundary
Disposition: `PREFERRED`
Mechanism: make `current_admission` the only public mutation root for writing-kernel current tasks. Legacy/historical compatibility remains a separate path. Every current mutation binds/validates current governance markers, requirement revision/digest, quality evidence, CAS/provenance and one execution receipt. Lifecycle/proactive/feedback helpers must enter this boundary rather than mutate current state directly.
Falsification: reject if this requires duplicating the workflow state machine, materially increases simple-task cost, or cannot preserve historical compatibility. Candidate implementation must prove otherwise.

### D — full event-sourced rewrite
Disposition: `REJECTED`
Reason: current state plus immutable receipt history already supplies most replay/provenance benefits; a full rewrite is larger than evidence requires.

### E — parent/host-only repair
Disposition: `REJECTED_AS_SUFFICIENT`
Reason: parent finalization can reduce response drift but cannot close confirmed child repository mutation/delivery provenance bypasses.

## Selected bounded intervention

1. Enforce one public mutation root for current writing-kernel tasks; weak owner_guard mutation paths must fail closed for current tasks or become internal-only primitives.
2. Current state validation must require Task Requirement Authority v1.0 and cannot silently disable it by stripping/changing its marker.
3. Every current mutation class (stage transition, feedback, proactive resolution, blocked recovery, system-impact lifecycle, requirement changes) must bind the active requirement revision/digest and current governance provenance before admission.
4. Add requirement-consumption evidence: a stage cannot claim compliance merely because its receipt carries a digest; it must record disposition/satisfaction for active requirements applicable to that stage/product.
5. Harden delivery provenance: canonical builder evidence must be bound to a builder-issued nonce/digest derived from the built artifact and build inputs; private research delivery must bind the admitted PrivateResearchBrief digest; stock-name normalization must match visible-text normalization; Audit and Interaction Pack need canonical builder paths.
6. Reconcile persistent architecture/evolution documents with production runtime after the implementation is proven.
7. Promotion requires exact-head CI plus no unresolved known review findings for the exact head used to merge. A changed head invalidates prior review evidence. Native GitHub branch protection is currently absent, so repository-level assurance must be reported accurately rather than overstated.
8. Migrate/replay the active cross-border task through the new requirement authority or explicitly replace it with a current-governed successor; do not rewrite historical receipts to fake compliance.

## Acceptance

- current tasks cannot mutate via a weaker public owner path;
- stripping/changing Task Requirement Authority marker fails closed;
- every current mutation receipt binds active requirement authority;
- stage/product requirement satisfaction is explicit, not inferred from digest presence;
- delivery evidence cannot be fabricated from caller-supplied PASS strings alone;
- private research visible copy is bound to the admitted brief digest;
- PRIVATE_RESEARCH and FINANCE_DEEP remain distinct in held-out/live replay;
- active/historical artifacts have one current namespace/cursor or explicit provenance status;
- exact-head CI + independent review/known-finding closure precede promotion;
- production reread and live successor/replay observation are required before closure.

## Assurance boundary

This domain refactor cannot create a physically non-bypassable ChatGPT pre-send/pre-tool hook. UAOS 2.8 owns the common behavioral/finalization policy; Financial owns its repository mutation/delivery integrity and must not use the native-host boundary as an excuse for domain-owned bypasses.
