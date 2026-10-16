# Editorial — Story Architecture Before Prose

Status: `CURRENT_CANDIDATE_1.0.3`
Owner: `DOMAIN:financial_writing`

## Purpose

Editorial converts audited cognition into a reader journey. It does not rewrite research, invent facts or dump the research directory into publication. The canonical object is `financial_writing_agent.story_quality.StoryBlueprint`.

## Form follows content

Compare genuinely different story engines when more than one is plausible. Current families include hard anomaly, company conflict, reversal, mystery/question, system map, consequence chain, `EVENT_TO_COMPANY`, character/case lead and timeline escalation. Named methods such as nut-graf/five-box/hourglass are candidates, not mandatory shells.

## StoryBlueprint requirements

A substantive long-form blueprint defines:
- reader job/start state, article promise, central question and author stance;
- chosen narrative engine;
- concrete opening anchor, information gap, financial stake, early payoff and unresolved later payoff;
- explicit contiguous Chinese H1 sequence (`一、二、三、...`);
- per-section reader question, new information, company/case anchors, value-chain classes, evidence refs, tension/open loop, payoff and bridge;
- ending payoff and voice evidence.

If a section cannot say what new information it adds, remove or merge it before drafting.

## Research completeness vs publication selectivity

Research must map the material value chain/company universe before thesis selection. Publication does not have to reproduce that map.

For `FINANCE_DEEP`:
- full publication coverage is legal only when editorial judgment genuinely needs all researched material classes;
- if any researched material class is omitted from copy, `publication_scope_decisions` must account for **every** researched class as `CORE`, `SUPPORT`, or `OMIT_WITH_REASON`, with evidence refs and rationale;
- CORE/SUPPORT must appear in the blueprint;
- OMIT_WITH_REASON remains in research provenance but must not silently become a publication branch;
- there is no default word-count ceiling.

Select by thesis contribution and reader value, not by the size of the research map.

## Comparative logic — Deep should explain why one path wins

For material multi-company or multi-branch research, Deep should preferentially publish the decisive comparison rather than a sequence of isolated company descriptions.

Use the admitted PrivateResearchBrief's within-segment comparison and `cross_segment_global_selection` to decide what comparison the reader actually needs. Typical forms include:
- same catalyst, different business stage: why A has realized revenue/profit while B is still planning/testing;
- same branch, different economics: why A has stronger pricing power, purity, order visibility, margin or cash conversion than B;
- different branches under one policy: why B2B/warehouse/payment/brand receives a stronger or weaker first-order transmission;
- economic winner vs market-recognition winner: why the strongest business and the fastest price-discovery vehicle may differ;
- durability comparison: which logic survives after the first news impulse and what would reverse that conclusion.

The prose should carry the causal reason for the ranking. Do not publish internal score tables merely to prove a comparison occurred. A sentence such as “A、B、C均受益” without explaining relative transmission is insufficient when the private research identifies a meaningful difference.

When current market liquidity means only one or a few narratives can dominate, Deep may explain the cross-branch economic contest — for example why one link captures more of the policy's profit transfer than another — without narrating tactical terms such as card-position, board height or next-day trade plans.

## Event-to-company causal grounding

A named company is not enough when the story is event-led. If the explanatory burden is how a rule/event/change reaches listed-company economics, use `EVENT_TO_COMPANY`.

Every material explanatory section then requires `causal_transmission` with:
1. `trigger_or_change`;
2. `mechanism`;
3. `company_exposure`;
4. `operating_or_financial_expression`;
5. `verification_or_reversal_condition`.

The prose order is flexible; the causal chain is not. This prevents abstract industry exposition followed by a decorative company list.

For policy stories, the event anchor must reflect the material chronology established in the private catalyst ledger. Do not write from a superseded policy phase while omitting a later suspension, reduction, extension, exemption, retaliation or rollback that changes the causal interpretation.

## Company comparison

Material companies need enough evidence to distinguish business economics, realization stage, sensitivity, evidence strength and adverse/change conditions. Comparative judgments may be explicit but remain evidence-bounded and non-actionable.

Deep should answer, where material, both:
- “why is A stronger/weaker than B inside this subsegment?”; and
- “after the subsegment winners are known, which business model/company has the strongest overall logic under this event, and why?”

If the evidence does not justify a single overall winner, preserve the competition and state the condition that would resolve it rather than manufacturing certainty.

## FINANCE_BROAD

Broad is an independent acquisition rebuild from the same audited evidence, not shortened Deep. It needs its own StoryBlueprint, opening/payoff path, company/case grounding, numbered H1s and PublicationFitness.

## Opening and continuation

The opening should orient a cold reader with concrete material while preserving a real unresolved payoff. Useful openings include a hard-number contradiction, two companies diverging under the same event, a rule change with an unintuitive consequence, a concrete case carrying the larger mechanism, or a reversal of a common assumption.

Each H1 answers one reader question, adds new information and creates a reason to continue. Do not spend the opening on generic importance statements, definitions the reader already knows or research-process narration.

## Ending

Close the central question with a usable mental model, distinction, verification framework or change condition. Do not end by merely repeating “未来值得关注/持续观察”.

## Editorial admission

Current-kernel tasks cannot leave `EDITORIAL` without required Deep/Broad StoryBlueprint(s). For selective Deep publication, omitted research classes require explicit scope accounting. For `EVENT_TO_COMPANY`, missing causal transmission blocks admission. Story planning is executable evidence, not a style-guide paragraph.
