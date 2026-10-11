# Financial Writing global system audit — 2026-10-12

Status: SYSTEMIC MAINTENANCE IN PROGRESS  
Scope: full Financial Writing owner architecture, execution routing, research/editorial/title/draft/audits, delivery, learning/evolution, quality promotion, continuity, tests/CI, and current user operating mode.  
Trigger: real failed article experiment + explicit global audit request.  
Current user operating mode: GitHub-mounted owner authority + GPT chat execution; Site/MCP deployment intentionally out of current scope.

## 1. Incident evidence
The real experiment demonstrated a severe owner-binding/runtime-trajectory bypass: the chat did not perform a capability handshake, did not create owner state, did not run Research/Editorial/Title/Audits, performed no current fact research, produced no Word/audit artifact, and still returned a pseudo-final article. The failure therefore begins before prose quality; it is not adequately fixed by adding more writing reminders.

The experiment also supplied a real negative live outcome: the user rejected the result as materially broken. That proves the output failed, but it does not prove any particular repair is correct.

## 2. System surfaces inspected
### Control/architecture
- `skills/financial-writing-agent/SKILL.md`
- `continuity/AGENT_MANIFEST.json`
- `continuity/EXECUTION_CAPABILITIES.json`
- `continuity/UNIVERSAL_PROTOCOL_ADAPTER.json`
- `continuity/TASK_INDEX.md`
- current Financial task manifest/handoff (read-only for this parent-maintenance writer)
- Universal v3.7 ENTRYPOINT, execution-readiness contract, agent-architecture contract, owner-adapter contract and system-maintenance policy

### Business semantics
- `references/research.md`
- `references/knowledge.md`
- `references/market_explanation.md`
- `references/editorial.md`
- `references/hooks.md`
- `references/style.md`
- `references/audit.md`
- `references/delivery.md`
- `references/platforms.md`
- `references/maintenance.md`
- `config/policy.json`
- `config/rule_ownership.json`

### Runtime/code
- models, schemas, routing, controller, engine, runner/runtime factory
- runtime service + SQLite store
- OpenAI stage adapter + semantic runtime
- deterministic delivery/mechanical checks + document builder/rendering
- MCP contracts/server
- system-impact + methodology receipt runtime
- quality-regression/promotion gate

### Harness/evidence
- CI workflow
- static audit and executable contract/smoke surfaces
- all owner test categories, with detailed review of trajectory, semantic proof, system-impact, execution-capability, quality-promotion and document/mechanical tests
- current GitHub Actions runner behavior

## 3. Triage findings
### CONFIRMED_DEFECT A — actual production execution mode was not first-class
Root-cause layer: `OWNER_BINDING / PRODUCT_CAPABILITY`.

The repository had a strong Python/owner-native workflow, while the user's real operating model is GitHub + GPT chat and there is currently no installed Financial owner plugin. Generation allowed CHAT_BRIDGED payloads, but durable workflow state, semantic audit progression and completion still assumed Python/plugin execution. This left a practical gap in which chat could ignore the declared handshake and jump directly to prose.

The defect is not “Site is missing.” Site deployment is optional/future under the user's current operating decision.

### CONFIRMED_DEFECT B — owner-native negative-feedback persistence had a crash window
Root-cause layer: `RUNTIME_OR_SCHEMA`.

`runtime_service.record_writing_learning_sample` persisted the raw sample before the plugin wrapper created the system-impact obligation and methodology receipt. A process interruption between those writes could leave a durable USER_REJECTION/USER_FEEDBACK/USER_EDIT without `PENDING_REVIEW`, violating the new v0.8.1 invariant.

Repair selected: enforce the immediate system-impact obligation at the SQLite persistence boundary. The first durable save of a latest negative/corrective sample now reconciles the missing signal before serialization. The later methodology receipt remains a separate self-attested evidence action and is not fabricated by persistence.

### CONFIRMED_DEFECT C — recent-task discovery has owner-native shadow logic
Root-cause layer: `RUNTIME_OR_SCHEMA`.

`runtime_service.list_recent_writing_tasks` hides all COMPLETE tasks by default, while the MCP wrapper separately preserves COMPLETE tasks carrying open maintenance obligations. These two entrypoints can therefore disagree on unresolved maintenance visibility.

Disposition in this change: OPEN / not silently claimed fixed. It is lower priority for the user's current GITHUB_CHAT production mode, but it remains an owner-native cleanup target. The canonical eventual fix is to move the filtering rule into one runtime authority and have the MCP wrapper delegate rather than reimplement it.

### CONFIRMED_DRIFT D — Universal Financial architecture observation is stale
Universal remote observation still points to old Financial head `a76c83...` even though Financial has moved through v0.8.1 and this repair branch. The old architecture PASS cannot certify the current owner head. Parent observation must be refreshed only after the final Financial head is known.

## 4. Investigated hypotheses that were NOT defects
### Agent architecture manifest version 1.0
NO_DEFECT. Universal Agent Architecture contract 1.1 explicitly supports manifest versions 1.0/1.1/1.2 through compatibility mappings. No gratuitous manifest bump required.

### Risk-disclaimer H1 apparent contradiction
NO_DEFECT. Delivery internally appends a risk-heading sentinel, while `document.py` intentionally consumes that sentinel without rendering a visible H1 and converts the following block into the final inline italic `风险提示：...` paragraph. Mechanical checks correctly reject a visible numbered risk heading.

### Quality-promotion gate too easy to self-certify
NO_DEFECT in the inspected contract. Promotion remains fail-closed on corpus readiness, immutable case bindings, real rejection/held-out diversity, candidate distillation, semantic evidence verification, bound hard-regression execution, blind position-swapped pairwise judging, and stronger positive/live evidence for personalized claims. Current corpora remain NOT_READY.

## 5. Alternatives considered
### Alternative 1 — add more reminders to Skill/account instructions
Rejected. The failed experiment already occurred despite repository rules requiring handshake/state/audits. This would repeat declaration-only control and increase hot-path text without creating a usable execution route.

### Alternative 2 — require Site/MCP deployment before Financial can write
Rejected for current scope. The user explicitly operates all agents as GitHub-mounted + GPT-chat and does not want deployment now. Treating deployment as mandatory would mis-model the product and unnecessarily block useful work.

### Alternative 3 — let chat self-review become semantic PASS
Rejected. This would solve usability by destroying the assurance boundary. Same-chat review may be useful, but it is not owner-native stage-separated execution or independent/provider-attested review.

### Alternative 4 — create a new Financial supervisor/reviewer Agent
Rejected. No distinct execution identity is gained; it would add architecture and review theatre without proving independence.

### Selected mechanism — explicit GITHUB_CHAT owner adapter
Reuse existing Universal `CHAT_BRIDGED` semantics and the already-proven pattern used by another GitHub-backed owner: GPT chat performs high-judgment work, GitHub is durable business state, action/review evidence is explicitly self-attested, and stronger assurance remains separate.

## 6. Implemented on maintenance branch
Branch: `maintenance/github-chat-runtime-20261012`  
PR: #12

- added `continuity/GITHUB_CHAT_EXECUTION.json`;
- execution capability profile 9 → 10 with explicit GitHub-chat workflow/review/delivery/learning paths;
- Skill now selects owner-native vs GITHUB_CHAT after current-session handshake and forbids free-form publishable fallback;
- GITHUB_CHAT persists per-article state at `workspaces/articles/{task_id}` and requires post-write reread;
- chat semantic review is `CHAT_SELF_REVIEW`, never native PASS;
- normal chat terminal state is `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`;
- article publication source remains durable in GitHub so transient Word attachments are reproducible;
- material chat-mode corrective/negative feedback must persist learning evidence + OPEN system-impact item together and must not fabricate owner-plugin receipts;
- Universal adapter and continuity index now understand the current user operating mode;
- architecture/README updated to one-owner/two-adapter model;
- SQLite persistence boundary now prevents the latest material negative/corrective sample from first being stored without `PENDING_REVIEW`;
- new contract/regression tests cover anti-bypass, stage evidence, assurance separation, negative-feedback durability and persistence idempotency.

## 7. Second-order review of selected repair
### Does it create a second business-rule authority?
No by design. Research/editorial/style/audit/delivery semantics remain in existing references/policy/runtime. `GITHUB_CHAT_EXECUTION.json` owns only execution-mode adaptation: state location, stage checkpoint obligation, session capability requirements and assurance mapping.

### Does it bloat the hot path?
The Skill remains under the existing 8192-byte router budget (measured branch blob size 7083 bytes). Detailed chat-mode mechanics are cold-path in the adapter contract.

### Does it weaken native semantic PASS?
No. Python/MCP PASS rules remain unchanged. Chat review has a different label and different terminal claim.

### Does it freeze unrelated owners?
No. This is Financial-owner-local execution repair plus later parent observation refresh.

### Can the new mode still be bypassed by a noncompliant chat model?
No repository-only design can physically prevent a language model from emitting text. The improvement is that the actual supported session now has a complete, usable execution path rather than an impossible runtime prerequisite. The remaining product-level proof must come from a real fresh article trajectory in the Financial chat. That is an explicit open gate, not hidden.

## 8. Validation state
### Structural / branch evidence
PASS for implemented-file existence, branch tree identity and measured Skill size. Contract tests are present and bound to the new profile/adapter.

### GitHub Actions
BLOCKED externally. PR run `38161149459`, job `114534150569`, again ended with no workflow steps (`steps=null`). Therefore none of SDK smoke, MCP smoke, pytest, contract eval, static audit, wheel install or DOCX render may be claimed as PASS for this branch.

### Live GITHUB_CHAT article trajectory
OPEN. This repair was triggered by a real failed chat trajectory, but no post-fix real article has yet executed the new `STATE.json → staged artifacts → chat reviews → Word → bounded terminal state` path.

### Live writing outcome
OPEN. The pre-fix user rejection is failure evidence, not post-fix success evidence.

### Independent/provider-attested audit
OPEN / unavailable by current product setup; intentionally not simulated.

## 9. Assurance ceiling
Current repair assurance ceiling before CI/fresh article evidence: `WIRED + STRUCTURALLY_REVIEWED`, with targeted persistence invariant encoded and contract tests added but not executed by a functioning GitHub runner.

Do not call this branch `REGRESSION_VERIFIED`, do not claim the new GITHUB_CHAT path already produced a good article, and do not claim global system perfection.

## 10. Next evidence that should close the highest-value gates
1. Merge only after final diff/reread is coherent and no known structural contradiction remains; CI remains explicitly blocked if runner still unavailable.
2. In the normal Financial chat, request a real article without saying “run the evolution system.” It should autonomously select GITHUB_CHAT, create GitHub article state before research, perform and persist every stage, deliver Word with an explicit bounded QA state, and record any correction durably.
3. Reobserve the final Financial owner HEAD from Universal and refresh the stale architecture observation.
4. When GitHub Hosted Runner becomes usable, rerun the unchanged full owner CI and only then promote repository assurance to `REGRESSION_VERIFIED` if every real step passes.
5. Separately repair the owner-native `list_recent_writing_tasks` shadow filtering and add a regression that a COMPLETE article with unresolved maintenance remains discoverable through every owner-native entrypoint.
