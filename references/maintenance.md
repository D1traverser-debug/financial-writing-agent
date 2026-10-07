# Maintenance module

Maintenance is not a second writing rulebook. It is invoked only when a durable rule changes, an external platform/tool/regulatory fact changes, or the system exposes a repeatable execution defect.

## Classify before changing anything
Every feedback item belongs to one primary class:
- `TASK_OVERRIDE`: valid only for the current task. Keep it in the current TaskContract/state; do not promote it into durable policy.
- `STABLE_RULE`: an explicit durable writing requirement. Update exactly one canonical owner and the affected executable contract/test boundary.
- `PLATFORM_METHOD`: recommendation/search/click/retention/account-behavior knowledge. Keep it in the platform/experience layer until current/repeated evidence justifies stronger promotion.
- `EXPERIENCE_SAMPLE`: one article's result, one viral/failing example, or one user reaction. Store as an experience sample; do not turn it into a universal formula.
- `SYSTEM_ERROR`: the rule already existed but execution skipped it, routing loaded the wrong thing, a gate falsely passed, or the wrong artifact/source identity was used. Repair execution/trajectory/tests; do not duplicate the same semantic rule in more files.
- `EXTERNAL_CHANGE`: platform rules, regulations, tool capabilities or external APIs changed. Reverify the current authoritative source before changing durable behavior, and retire stale assumptions explicitly.

Accepted style edits may inform the anti-AI/style library, but one article must not become a rigid template.

## Single semantic owner
The same semantic requirement should have one authoritative owner. Other files may route to it, expose an observable acceptance result, or test it; they should not develop parallel prose versions that can drift.

Current ownership pattern:
- runtime/control: stage order, checkpointing, task isolation, required outputs, invalidation and fail-closed behavior;
- research: what must be known, source/evidence standards, coverage, StockBase read-only/review queue;
- editorial/style: topic-specific selection, structure, hooks, prose, anti-AI and author stance;
- delivery: publication compliance, Word/format/artifact mechanics;
- audit: how the final state proves those existing rules actually held;
- platforms: changing distribution mechanics and account/platform evidence;
- knowledge: reusable cognition and writeback boundaries;
- maintenance: change classification, owner migration and regression discipline.

## Learning persists; task state does not
Durable learning may survive across tasks: verified event/industry/company cognition, source-quality notes, reusable evidence, accepted platform experience, style lessons, failure-prevention rules and regression cases.

A genuinely new task must not inherit an old task's stage, blockers, selected title, selected outline, draft, artifacts, pending actions, visual package, checkpoint or “next step” merely because that task exists. Only an explicit resume/continue intent may restore persisted task state. New-task knowledge recall may reuse durable cognition, but reusable knowledge is not equivalent to continuing the old job.

This separation is a hard anti-contamination principle for cold start: **inherit learning, not unfinished work**.

## Change protocol
1. Identify the feedback class, canonical rule owner and affected runtime stages.
2. For `SYSTEM_ERROR`, first explain why the existing rule/gate failed before writing new wording; prefer repairing the execution boundary/test over adding duplicate instructions.
3. Modify the canonical skill reference/runtime contract. High-judgment behavior should gain decision criteria/failure conditions; low-judgment behavior should become deterministic schema/gate/check assertions where practical.
4. Search contradictory/duplicate legacy wording, old names and opposite defaults. Retire or convert stale copies into references rather than leaving both semantics live.
5. Check whether routing/Skill loading conditions need to change. If not, do not touch them merely because another rule changed.
6. Check whether audit needs a new **observable outcome/evidence requirement**. Audit should not re-copy the method prose.
7. Synchronize intentional runtime/reference mirrors and require byte-for-byte CI equality where the repository declares mirrors.
8. Add/update regression tests and trajectory assertions for the easiest recurrence path.
9. Run the regression as if the next conversation has **none of the current chat's working memory**: only packaged Skill/references, persisted runtime/knowledge and the new user input may be assumed.
10. Run unit, static, contract and trajectory tests plus package/install smoke; run representative live writing/image-delivery tasks when behavior depends on model/tool execution.
11. Read back the changed owners and search for retired semantics again.
12. Promote only after readback/regression pass.

A documentation edit is not proof that an Agent executes the behavior. Runtime traces, files and audit evidence are proof. Likewise, the existence of a Skill file is not proof that every possible ChatGPT entry point automatically loads it; activation/hosting behavior must be tested in the actual target environment before claiming zero-reminder execution.

## High-judgment vs low-judgment changes
Titles, TopicDNA, structure, hooks, emphasis and prose are high-judgment domains. Improve their evaluation dimensions, evidence requirements and failure conditions rather than accumulating universal sentence templates.

File identity, required outputs, stage order, StockBase permissions, Word styles, checksums, gate state and source/count reconciliation are low-judgment domains. Prefer explicit schemas, programmatic assertions and fail-closed gates over reminders in prose.

## Error learning without false claims
When an existing gate should have caught a defect, record enough information to reconstruct: error type, symptom, root cause, where detected, why the gate missed it, detection rule, prevention rule and affected regression. Repeated independent failures should increase test/gate strength.

Do not claim that automatic cross-task recurrence counting or L0 promotion exists unless the runtime actually persists and enforces such a ledger. Until then, the durable maintenance/regression record is the authority for preventing recurrence.

## Completion condition for maintenance
A maintenance change is not complete until:
- classification is explicit;
- one canonical owner has the new semantics;
- contradictory/duplicate old semantics are removed or clearly superseded;
- routing references remain valid;
- affected acceptance evidence is updated without duplicating method rules;
- regression coverage exists;
- cold-start reasoning does not rely on the current conversation;
- the modified files are read back and mirrors are synchronized;
- any behavior not yet executable/tested is labeled as such instead of being advertised as implemented.
