# Financial Task Requirement Authority

Status: candidate
Owner: `DOMAIN:financial_writing`
Contract: `financial_writing_agent.task_requirements` 1.0

## Problem being closed

Material task requirements were previously classifiable in product requirements but not represented as first-class owner authority. A requirement could exist in chat or `feedback/*.md`, be observed by one stage, and still be absent from the canonical article state consumed by a later stage. That allowed requirement drift without violating the old state schema.

The live `cross-border-ecommerce-20261016-v2` task supplied direct evidence: a current task-specific requirement file existed in the workspace while `STATE.json.source_refs` still pointed only to older task feedback. Later generation could therefore follow recent chat context or stale publication assumptions instead of a mechanically bound requirement revision.

## Governing distinction

User feedback is evidence. A task requirement is authority only after it is admitted into the task Requirement Authority. Domain/global rule promotion remains a separate evolution decision.

This prevents two opposite errors:

1. treating every user sentence as an immediate global rule;
2. treating explicit task requirements as disposable chat context.

## Authority object

Current Financial tasks created after this change carry:

- `task_requirement_contract_version`;
- `task_requirement_authority`;
- `task_requirement_digest`.

The authority contains a monotonic `revision`, the active requirement set, and immutable change history. Each active requirement records:

- stable `requirement_id`;
- exact normalized statement;
- product/stage scopes;
- earliest affected workflow stage;
- evidence reference;
- source kind.

## Requirement-change transaction

`financial_writing_agent.current_admission.apply_task_requirement_change` is the owner-native mutation entrypoint.

A change:

1. validates the previous owner state;
2. applies add/replace/retire semantics without silently deleting unrelated requirements;
3. increments the requirement revision;
4. recomputes a canonical digest;
5. determines the earliest affected Financial stage;
6. invalidates that stage and downstream derived evidence when the task has already progressed past it;
7. appends a durable `github_chat_requirement_governance` execution receipt;
8. preserves task scope and does not promote the requirement into Financial-wide policy.

## Stage inheritance

Every subsequent current-admission state mutation binds:

- requirement contract version;
- current requirement revision;
- current requirement digest;
- canonical requirement authority path.

`requirement_context_for_scope` returns the exact active requirements a research/product/delivery pass must consume. This is the stage input; chat memory and ad-hoc feedback search are not substitutes.

## Recovery semantics

Requirement changes invalidate from the narrowest declared affected stage. Examples:

- research universe/private-research coverage change -> `RESEARCH`;
- Deep/Broad story architecture change -> `EDITORIAL`;
- prose-only requirement -> `DRAFT`;
- Word presentation requirement -> `DELIVERY`.

The user does not need to manually request invalidation. The requirement transaction owns it.

## Assurance boundary

This control closes a Financial-domain authority gap. It does not prove native ChatGPT host-level non-bypassable pre-send mediation; that remains parent/common scope when required.
