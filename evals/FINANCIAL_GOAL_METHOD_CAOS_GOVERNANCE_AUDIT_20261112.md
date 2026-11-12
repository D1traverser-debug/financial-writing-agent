# Financial Writing — CAOS-method governed system reconstruction (2026-11-12)

Scope: **Financial Writing-only system engineering**. CAOS source/Skill was consulted strictly read-only (observed CAOS main `9686cedeb3fd8171ecf70eab33aaea641217b04a`); no CAOS code, PR, branch, settings, Host, plugin or article content was changed. The owner explicitly prioritizes Financial's intrinsic requirements, decision/execution/recovery, methodology CRUD, governance and testable architecture over any real article production.

## Complete owner demand, preserved without the last-patch substitution

1. CAOS should **direct the redevelopment method**; the eventual Financial plugin/client must work independently, with one Financial owner and one `main`. CAOS is **not** an installed Financial runtime controller.
2. Recover the user's original demands and corrections; separate hard instruction, correction, preference, tentative suggestion, proposed fix, issue/failure observation and unverified model inference. Do not silently delete or overwrite an earlier requirement.
3. Decisions must challenge their own route/tool/source/root-cause method, compare reuse/adapt/replace/remove/build, perform bounded external/current evidence investigation, verify counterexamples, and reopen contradicted diagnoses recursively.
4. Execution must persist legal state transitions, authenticated grants, precise resource/provider bytes, evidence-bounded stage artifacts, invalidation and repair loops, independent checks and OPEN obligations.
5. Methods and knowledge require **add/read/revise/promote/challenge/retire/restore** with provenance, version, applicability, counterexamples, independent promotion and impact revalidation; deletion is non-destructive retirement, not erasure of source history.
6. Use the existing `knowledge/METHOD_KNOWLEDGE_CATALOG.json`, `evals/EVOLUTION_INDEX.json`, the Financial Skill and the per-article state as authority. No second Financial task ledger, no CAOS writes. Historical provenance remains unchanged.

## Root-cause alternatives — evidence and falsifiers

| Hypothesis | Evidence observed | Discriminator | Disposition |
| --- | --- | --- | --- |
| Just improve prompts/skill text | Existing Skill already describes goal recovery and method evolution | Try real transport operations and source binding | Rejected as sufficient; runtime had no method lifecycle |
| Add an external CAOS parent controller | CAOS supports richer recursive decisions | Check if Financial has one canonical article state and existing knowledge/evolution owners | Rejected: violates standalone connection and risks split authority |
| Rebuild the Financial task state schema from scratch | Existing TaskRequirement v1 has revision, history and stage invalidation | Simulate corrections and old receipts | Rejected: needless provenance break |
| Extend existing Financial authorities with authenticated intent and bounded method governance | `TaskRequirement.source_kind` defaulted to `USER_EXPLICIT`; knowledge catalog has 14 descriptive records but no CRUD API; new method cannot be independently admitted or retired through a provider port | Negative tests for suggested text, forged author, stale CAS, pending adoption, retired rule, missing impact evidence | **Selected**, preserving one owner and append-only provenance |

The selected solution was rechallenged against legacy catalog readability, owner-source authenticity, stale/CAS and fake approval, full article workflow compatibility, active-method silent replacement and the need to close impact reviews without erasing old events.

## Native Financial responsibility graph (recursive, not a fixed checklist)

`USER INPUT / AUTHENTIC CORRECTION` → owner intent evidence (original text, role, SHA-256) → `REQUIREMENT` or `NONBINDING` classification.

- `USER_REQUIREMENT / USER_CORRECTION / USER_PREFERENCE`: source-authenticated changes route to the **existing** `TaskRequirementAuthority` and stage invalidation graph. The source quote is proven present but not published in the repo; receipt stores source/excerpt digests and classification assurance. A correction may replace or retire, with the original preserved in history.
- `USER_SUGGESTION / IMPLEMENTATION_IDEA / ISSUE_REPORT / ASSISTANT_INFERENCE / UNKNOWN`: never become active task requirements. They are recorded as OPEN nonbinding events in the **same article state**, using authenticated original user-message readback. A reported root problem still requires the existing feedback/system-impact decision process; a proposal is not an automatic global rule.
- `DECISION`: existing `DecisionEnvelope` for material choices; independently checked alternatives, counterexamples, source kinds, scoped saturation, rejected routes and falsifiers. A model classification or source hash alone is not proof of semantic intent.
- `METHOD CATALOG`: `CREATE` adds CANDIDATE, `REVISE` adds pending revision without replacing effective old method, `DISCARD_PENDING` rejects a tentative revision, `PROMOTE` requires trusted independent provider verification of exact record SHA and validation refs, `CHALLENGE` excludes the disputed method from operational selection, `RETIRE` tombstones without deleting history, `RESTORE` returns only to CANDIDATE.
- `METHOD IMPACT`: every change records affected Financial stage names and an OPEN revalidation obligation. `VERIFY_IMPACT` requires authenticated independent stage-evidence verification for **all** affected stages; it appends a closure event, preserving the OPEN historical event. Old observations are not rewritten. Real end-user/article outcome remains a separate gate.
- `EXECUTION GRAPH`: unchanged canonical ten-stage owner workflow; existing review failure cursor, recovery, proactive resolution, system-impact review and exact resource/admission gates remain in place. Contradictions reopen earliest affected evidence, not an unrelated local workaround.
- `CONTINUATION`: `observe_article` exposes active requirements, open nonbinding owner intents, unresolved system impacts, stage and next action; `observe_method_catalog` returns method status plus outstanding revalidation events.

## Authority and trust boundaries

- Input: an LLM-supplied `USER_EXPLICIT` label, message URL or quote is insufficient. The Financial client must actually supply `owner_instruction_reader` backed by authenticated original user messages. The deterministic check proves source role, exact text, SHA and quote presence; **it does not prove all semantic nuances of user intent**.
- Write: `admit_article_action` is the one article-state provider port. `admit_method_action` is a method-authority scope of the **same Financial domain**, writing only `knowledge/METHOD_KNOWLEDGE_CATALOG.json` under user authorization, exact expected Git Blob CAS, reread and byte identity; it is not a second controller or task index. Any missing provider/authentication blocks only the affected action.
- Global rules: a user correction to one article cannot silently become a method or global writing rule. Method changes need material DecisionEnvelope evidence beyond user opinion, source-family method evidence, alternative analysis, external promotion and later impact revalidation. Old catalog entries are `LEGACY_DECLARED`, **not automatically independently verified**.
- Outputs: self-assessed source/method facts and green CI cannot establish product quality, original user-message authenticity in a real ChatGPT client, native activation, or reader acceptance.
- Historical: old records and receipts remain provenance. No direct CAOS/UAOS invocation is introduced.

## Engineering checks / negative regression

Core suites:
- `tests/test_financial_goal_intent_governance_20261112.py`: missing source kind; suggestion modeled as command; forged assistant/user role; unknown source; bad digest/quote/source ID; explicit correction preserving requirement revision; nonbinding idea record without silently mutating active requirements; ambiguous retire+upsert refusal.
- `tests/test_financial_method_governance_20261112.py`: legacy catalog read; candidate not active; staged revision without overwrite; fake/self review refused; provider-sourced promotion; challenge/retire/restore history; impact close negative and externally attested positive; no CAOS/article write; authorization denial, stale CAS, forged write, second-read mismatch.
- Existing 346+ Financial article graph, research, delivery, static, wheel and Word render tests remain relevant and must all PASS at exact branch head before promotion.

Assurance = `ENGINEERING_REPLAY_WITH_SYNTHETIC_TRUSTED_PROVIDER`. Real ChatGPT user-message origin, actual provider activation, external reviewer identity and reader outcome = `NOT_TESTED`. This is the **user-selected engineering scope**, not a request to produce a real article. Changed code must be promoted only after exact-head CI, defect scan and post-main independent reread.

## Residual architectural risk / falsifiers

- When the real Financial client cannot supply an authenticated original user-message reader, `CHANGE_REQUIREMENTS` must remain blocked rather than bypassing source verification. A verified real source-reading connector is a separate integration milestone, not an implied install.
- Method change events carry affected stages and an explicit revalidation obligation, but current existing articles do not automatically all become invalidated merely because a catalog changes; the live provider must use those obligations for affected article review. **No claim of cross-article live dependency propagation** is made until a real provider effect is independently read back.
- Future verified method promotion must not be spoofed by a model-written PASS or a synthetic callback. Only externally authenticated results justify adoption.
- A real owner intent may be semantically ambiguous even when the quote is byte-perfect; the system must keep the clause as a proposal/UNKNOWN and challenge classification rather than guessing.
