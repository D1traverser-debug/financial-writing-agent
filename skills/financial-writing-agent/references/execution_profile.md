# WritingExecutionProfile — Decision-Domain Construction

Status: CURRENT_FINANCIAL_OPERATING_REFERENCE  
Scope: every Financial Writing task and every requested product.

## Purpose

Keep the business process invariant while making only user-authorized decisions fixed. Everything not actually constrained by an active user requirement remains open to evidence, subject matter and reader needs.

This profile is a derived execution context. It is not a second requirement authority, a whole-task classifier, a router or a new workflow.

## Construction order

1. Read the complete original user prompt, current task state, active TaskRequirementAuthority, corrections and supplied materials.
2. Preserve negation, exclusions, named entities, audience, product and delivery requirements. Do not infer exclusivity from a mention.
3. Separate active `USER_EXPLICIT` and `USER_CORRECTION` requirements from `USER_PREFERENCE`. Suggestions, hypotheses and implementation ideas are not hard requirements.
4. Create a scoped `decision_domains` record for each meaningful decision:
   - `LOCKED`: cite one or more active explicit/corrective requirement IDs.
   - `OPEN`: cite no hard requirement IDs. Preference IDs may guide the choice without locking it.
5. Map every active fixed requirement and preference to at least one domain. Do not widen a domain's scopes beyond the cited requirement scopes.
6. List conditional modules only when they are material to the current task. Do not activate full-universe, market-role, policy-transmission or other specialist research merely because a generic template contains them.
7. Bind the profile to the exact original prompt SHA-256 and current requirement projection. Every semantic pass receives the same profile.
8. If a user requirement changes, refresh the profile and invalidate all affected downstream evidence before continuing.

## Decision-domain semantics

Each record contains:
- `domain`: a descriptive decision area, not a closed taxonomy;
- `disposition`: `LOCKED` or `OPEN`;
- `scopes`: the exact TaskRequirement scopes affected;
- `requirement_ids`: explicit/corrective IDs that justify a lock; empty for OPEN;
- `preference_ids`: preferences that may guide the decision but never create a lock;
- `rationale`: concise explanation of why the domain is locked or remains open.

A `LOCKED` domain without an active hard requirement is invalid. An `OPEN` domain with a hard requirement ID is invalid. The same domain may have different dispositions in different product scopes only when the scopes do not overlap.

## Important distinctions

- A topic mention locks the subject, not the thesis, company universe, title or article structure.
- “关注 A、B、C” makes those companies research candidates/anchors; it does not automatically mean “only these companies” or “all must appear in publication.”
- “只比较 A、B、C” locks the comparison scope. Do not silently expand the requested comparison universe.
- “根据这个立意” or a user-supplied causal story locks the research focus/question to investigate, not the truth of the conclusion. Test it against current evidence and counterexamples.
- A user preference such as “更简洁” may guide an OPEN style/length domain; it must not become a hard prohibition or fixed word-count rule unless the user explicitly says so.
- The user may lock the output contract while leaving narrative engine, title angle, opening, section order, paragraph rhythm and technical depth open.

## Cross-topic diagnostic examples

These examples are expected semantic distinctions, not article templates:

| Task prompt | Locked domains | Open domains |
|---|---|---|
| “冰雪经济 / 你做吧” | TOPIC_SCOPE | COMPANY_UNIVERSE, THESIS, NARRATIVE_ENGINE, TITLE, SECTION_ORDER, VOICE |
| Huangjiu high-end channel with a supplied distributor thesis | TOPIC_AND_CHANNEL_FOCUS, WORKING_HYPOTHESIS_TO_TEST | FINAL_CAUSAL_CONCLUSION, COMPANY_UNIVERSE, PUBLICATION_SELECTION, STORY_FORM |
| Meta Muse Wonder with six supplied A-share candidates | TOPIC_EVENT, RESEARCH_CANDIDATES, RESEARCH_FOCUS | COMPANY_CLASSIFICATION, FINAL_CAUSAL_CONCLUSION, PUBLICATION_SELECTION, STORY_FORM |
| AI-security prompt naming three companies and a spending thesis | TOPIC_SCOPE, RESEARCH_CANDIDATES, RESEARCH_QUESTION | FINAL_CAUSAL_CONCLUSION, COMPANY_CLASSIFICATION, STORY_FORM |

These are CHAT_SELF_REVIEW diagnostic annotations. They do not certify the live model's semantic classification or independent editorial quality.

## Failure conditions

Reject or rebuild the profile when:
- a locked domain has no explicit/corrective requirement ID;
- an open domain carries a hard requirement ID;
- any active requirement or preference is unmapped;
- a domain scope exceeds the scope of the requirement that justifies it;
- one domain is simultaneously locked and open over overlapping scopes;
- a preference is promoted to a lock;
- the profile prompt hash or requirement projection is stale.
