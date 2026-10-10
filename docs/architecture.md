# Financial Writing Agent — Architecture v0.5

## 1. Goal
Build a reliable A-share financial-writing system that develops broad/deep cognition before expression, explains both economic benefit and market selection when stock/theme price behavior matters, designs the full reader funnel rather than isolated hooks, learns durable Writing DNA with provenance, produces publication-ready Word artifacts, and proves completion through independent semantic and mechanical gates.

## 2. Core architecture
The system uses a **deterministic outer runtime with model-driven inner stages**.

Deterministic Python owns TaskContract routing, legal state transitions, checkpoint/resume, fail-closed behavior, required Word outputs, Word construction, exact typography, mechanical/render checks and completion authority.

High-judgment model work owns current research synthesis, TopicDNA, market-explanation hypotheses, mode-specific reader framing, Reader Funnel design, editorial structure, title generation, drafting, Natural Authorial Prose judgment and final semantic red-team.

## 3. Runtime graph
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Mandatory failures route to `BLOCKED`; there is no fallback edge to ordinary free-form writing.

## 4. Content modes
Financial Writing owns `FORMAL_ARTICLE` only.

Unspecified platform defaults to `DUAL`: one audited research base, independently edited `FINANCE_DEEP` and `FINANCE_BROAD` versions.

- `FINANCE_DEEP`: material-complete relative to the bounded audited research universe; prioritize qualified finance-reader fit rather than forced maximum reach.
- `FINANCE_BROAD`: traffic-oriented selective compression around one to three information gaps while preserving evidence strength and counterevidence; broader-finance relevance is useful when real, not mandatory when forced.

Delivery is `WORD_FILE_ONLY`. There is no chat-text article artifact, visual package, sticker post, image insertion or image resource surface.

## 5. Research and market explanation
Research covers event chronology, concept/subtheme map, industry/transmission chain, relevant A-share universe, company fundamentals/business stage, counterevidence and current market structure when material.

For stock/theme/price-reaction topics, research separates:
1. **economic benefit / realization** — who is exposed, through what business path, with what sensitivity and timing;
2. **market selection / price formation** — why attention, price discovery or order flow selected one stock/subtheme earlier or more strongly than peers.

Market explanation is multi-hypothesis rather than a fixed hindsight chain. Material explanations use:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

Price action proves that a selection occurred; it does not prove its own cause.

## 6. Reader Funnel assurance
CTR, title hooks, reader profile, first-screen retention, H1/paragraph continuation and completion are one funnel:
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`.

The dedicated Reader Funnel / Hook Gate checks:
- audience-promise fit;
- headline information value;
- curiosity/concreteness balance;
- current WeChat search discoverability;
- first-three-sentence retention;
- continuation flow across H1s and paragraph transitions;
- completion payoff;
- title/opening payoff.

Cross-industry finance clickability is not a universal hard rule. Account-level behavior, repeated user feedback and mode-specific reader fit outrank generic reach heuristics. Demographics and device-price clues are weak priors unless observed behavior supports the inference.

## 7. Natural Authorial Prose and Writing DNA
“去AI味 / 活人感 / 娓娓道来 / 交流感” are treated as overlapping symptoms of one authorial-writing system, not separate stylistic tricks.

The independent prose gate checks nine dimensions:
1. fidelity and responsibility;
2. semantic contribution;
3. argument progression;
4. reader calibration;
5. authorial selectivity;
6. evidence specificity;
7. structural/rhythm naturalness;
8. template/redundancy control;
9. uncertainty/rhetoric calibration.

Writing DNA learns with provenance. Explicit durable user instructions are direct rules; repeated independent accepted changes and broad user-corpus patterns can support promotion; one-off edits and external skills remain candidates. External benchmarks contribute abstract principles, not copied signature language.

## 8. Editorial assurance
Structure comes from current TopicDNA rather than reusable article templates. FINANCE_DEEP completeness obligations are derived from audited research and may not omit material branches merely for elegance or brevity.

The frozen draft must pass three independent semantic judgments before completion:
1. Reader Funnel / Hook Gate;
2. Natural Authorial Prose / Writing DNA Gate;
3. general editorial audit.

## 9. Delivery architecture
Only Word artifacts are public deliverables:
- `FINANCE_DEEP.docx` when deep mode applies;
- `FINANCE_BROAD.docx` when broad mode applies;
- `WRITING_AUDIT_REPORT.docx` always.

The only MCP artifact resource template is `writing-docx://{task_id}/{kind}`.

Word typography is deterministic:
- H1 `24px = 18pt`;
- H2 `20px = 15pt`;
- body `18px = 13.5pt`;
- H3 currently `12pt`.

Publication tables are prohibited. Company names and explicit skim-path anchors are bolded and mechanically checked under the current delivery policy.

## 10. Persistence and authority
- GitHub `main`: executable code/rule truth.
- Hosted durable store: per-task checkpoint truth when a Site runtime exists.
- SQLite: local/CI reference implementation.
- Notion/Drive: optional governance/knowledge layers, not executable checkpoint authority.

v0.5 is a hard schema cutover from v0.4 reader/style payloads. It continues the earlier removal of old Site PoC, `CHAT_TEXT`, visual/sticker and MCP compatibility-shim contracts.

## 11. Public MCP surface
`financial_writing_agent/plugin_server.py` is the single MCP registration surface. `runtime_service.py` owns business/runtime operations and must not register a second MCP server. The former `mcp_server.py` compatibility shim is deleted and must not return.

## 12. Assurance classes
1. Deterministic assertions: transitions, schemas, required outputs, hierarchy, exact typography, zero tables, file identity and render/mechanical checks.
2. Independent semantic judges: research completeness, market explanation, Reader Funnel, Natural Authorial Prose / Writing DNA, platform fit and compliance.
3. Trajectory/eval tests: stage order, fail-closed behavior and downstream invalidation.

Passing one class never substitutes for another.

## 13. Promotion rule
A future private Site deployment must implement the current v0.5 contract directly. It must not revive v0.4 headline/audit schemas, the removed 16-tool PoC or any legacy text/visual compatibility surface. Production-ready status still requires a user-authorized real-article E2E with interruption/recovery and fresh-chat artifact recovery.
