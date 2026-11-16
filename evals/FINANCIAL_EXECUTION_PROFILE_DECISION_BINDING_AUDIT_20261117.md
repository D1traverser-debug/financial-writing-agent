# Financial Writing — Execution Profile Decision-Binding Audit

Date: 2026-11-17  
Scope: all Financial Writing tasks; fixed workflow, user-locked requirements, preferences and open editorial decisions.  
CAOS: no CAOS source, configuration, Skill, PR or runtime is modified.

## 1. Product-level finding

The system has one canonical ten-stage workflow and a prompt-bound WritingExecutionProfile. The remaining defect is not another workflow gap. It is a traceability gap inside the execution profile: active hard requirements and preferences are validated as exact ID sets, but the profile's locked/open domain labels are not linked to those IDs.

## 2. Reproduction

Under the previous schema, both of these could pass structural validation:
- `fixed_requirement_ids=[]`, `locked_decision_domains=["COMPANY_SCOPE"]`;
- an active explicit requirement `only_compare_three_named_companies` exists, but the profile omits any locked company-scope domain.

The validator checked unique/disjoint domain strings and exact requirement-ID projections independently. It never checked the relationship between them.

This permits false locks and missing locks. Because every semantic pass receives the same profile, a mistaken lock/open classification can propagate through research, editorial, title, draft and audit.

## 3. Cross-topic counterexamples

| Real task | What is locked | What must remain open |
|---|---|---|
| Ice/snow economy, 2026-10-13 | Topic focus | Company universe, thesis, narrative engine, title, section order and voice |
| Huangjiu high-end channel, 2026-10-15 | Topic/research focus and user-supplied working hypothesis as a question to test | Final causal conclusion, company universe, publication selection and story form |
| Meta Muse Wonder / A-share AI, 2026-10-13 | Event focus, named research candidates and requested research direction | Company classification, final causal conclusion, publication selection and story form |
| AI security / AI data-center security, 2026-10-11 | Topic, named research candidates and the question whether AI expands security spending | Whether the proposed thesis is supported, company classification, title and narrative form |

These examples are diagnostic semantic annotations derived from actual Financial task STATE prompts. They are not independent editorial evidence and do not prove live model execution.

## 4. Alternatives and selection

- More prose-only instructions: rejected; they do not make the authority relationship checkable.
- Keyword-based prompt classifier: rejected; it would over-regularize open-ended tasks and recreate whole-task routing.
- Scoped decision-domain bindings to existing TaskRequirementAuthority: selected; one workflow and one authority remain unchanged.

## 5. Candidate correction

WritingExecutionProfile 1.1 replaces unbound locked/open lists with scoped decision-domain records:
- `LOCKED` domains cite active USER_EXPLICIT or USER_CORRECTION IDs.
- `OPEN` domains carry no hard requirement IDs; preference IDs may guide them.
- Every active fixed requirement and preference maps to at least one domain.
- Binding scopes cannot widen beyond the scopes of their cited requirement IDs.
- A domain may be locked for one product and open for another only across non-overlapping scopes.

The TaskRequirementAuthority remains the sole source of binding requirements. Conditional modules remain task-materiality decisions; no new task taxonomy, workflow, router or state store is added.

## 6. Evidence boundary

CI and schema tests can prove structural authority bindings. They cannot prove that the model correctly classifies every user prompt, that the selected editorial strategy is effective, or that real articles are independently accepted. Live Financial Provider Action remains NOT_DEPLOYED. Real article execution, blind review and reader acceptance remain OPEN.


## 7. Mainline integration and exact-head verification

PR #89 was squash-merged to Financial `main` as `44eeaea6f871ed4006d7e98a36dd9375a5fc87ea`. The final PR head `fabdd6a0b41ffeaf509350720f3b8e370525bcb0` passed exact-head CI run [43922363378](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43922363378): 758 tests, 88% Python statement coverage. The merged main SHA passed exact main CI run [43924128311](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43924128311): 758 tests, 88% coverage; Portfolio Coordinator 90%, Standalone Runtime 89%, Writing Kernel 81%. Whole-tree audit: 351 tracked files, 137 Python AST parses, 55 JSON parses, 57,952 decoded text lines, zero warnings/errors.

No separate external technical review was obtained. The merge is an engineering integration, not independent acceptance. The four cross-topic profiles remain CHAT_SELF_REVIEW diagnostics. Real model semantic replay, independent editorial/reader review, live Financial Provider Action and fresh-session Skill activation remain OPEN. No CAOS source or runtime was modified.
