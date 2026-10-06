# Financial Writing Agent — Architecture

## 1. Goal

Build a financial-writing agent that can start from a fresh conversation, preserve research depth, adapt the article for different distribution contexts, produce Word deliverables, and prove completion through visible audit evidence.

The design objective is **reliable execution**, not a larger prompt.

## 2. Chosen architecture

The system uses a **deterministic outer runtime with model-driven inner stages**.

### Outer runtime — deterministic Python
Owns task routing and TaskContract, legal stage transitions, checkpoint/resume, retry/blocked behavior, required-output calculation, file existence and artifact identity, Word/mechanical checks, and the completion gate.

### Inner stages — high-judgment model work
Own source-grounded research synthesis, TopicDNA and thesis selection, article architecture, headline/hook generation, drafting, and semantic audit/red-team review.

Model stages return structured Pydantic outputs. They do not decide whether the workflow may skip a stage.

## 3. Runtime graph

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Any unrecoverable stage failure routes to `BLOCKED`. There is no fallback edge from `BLOCKED` to free-form writing.

## 4. Why plain Python + Pydantic instead of a workflow framework

The writing workflow is mostly deterministic and small enough that an explicit state machine is easier to audit than a general graph framework.

The runtime therefore does **not** depend on LangGraph/CrewAI/AutoGen for its outer orchestration. Their useful patterns were adopted—state, checkpointing, conditional edges, independent judges—without inheriting framework complexity.

OpenAI Agents SDK remains an optional adapter for high-judgment stages only. It can be replaced without changing the runtime contract.

## 5. Persistent layers

### GitHub — canonical executable source
Repository `D1traverser-debug/financial-writing-agent`, branch `main`, owns runtime code, tests/evals, reference policies, version history and CI.

### Notion Skill — discovery/bootstrap layer
Owns task trigger, runtime-first rule, canonical GitHub location and compact default contract. It must not become a second detailed specification.

### SQLite — per-run state
Stores TaskContract, current stage, gates/evidence, artifacts, trace and checkpoint/resume state.

### Cross-conversation pointer
SQLite is not sufficient for chat-level recovery. The external active-task pointer must be updated at material stage transitions and read back before a fresh conversation is declared recoverable.

### ArticleBase / long-term knowledge
Stores performance samples, platform observations, TopicDNA, accepted article learnings and other durable experience. One-off performance outcomes do not automatically become rules.

## 6. Tool policy

### Source acquisition
- Current-conversation files: Files connector first.
- Public/current information: web search / direct page retrieval.
- Google Drive material explicitly requested by the user: Google Drive connector.
- Firecrawl or browser automation: fallback when ordinary retrieval is insufficient, not a mandatory first step.

### Writing outputs
- Default delivery: `WORD_FILE_ONLY`.
- Word generation/checks: deterministic document code plus render/mechanical validation.
- Chat contains links/status only unless the current TaskContract explicitly sets `CHAT_TEXT`.

### Long-term maintenance
- `main` is the code truth.
- CI must pass before executable behavior is considered healthy.
- A real article regression is required for major runtime changes.

## 7. Distribution model

Research is done once at full topic depth.

- `FINANCE_DEEP`: finance-community version; preserves fuller causal chain, universe competition, why-this/why-not and market-selection reasoning.
- `FINANCE_BROAD`: broad-distribution version that remains a financial article; it translates sector-specific events into finance-wide questions without flattening the reasoning.
- `DUAL`: one research base, two independently edited articles.

There is no fixed word-count target.

## 8. Editorial model

The agent does not rotate fixed article templates.

1. Build TopicDNA from the current topic.
2. Generate multiple candidate structures.
3. Use structure patterns only as optional design patterns.
4. Select/combine based on the current article's core contradiction.
5. Only after the current outline exists, use recent-outline fingerprints as collision checks.

Headline work is a separate high-judgment hook stage. A headline is judged on finance relevance, primary contradiction, factual anchor, information gap, cognitive load and body payoff.

## 9. Assurance model

Three assurance classes are intentionally separate:

1. **Deterministic assertions** — stage order, required outputs, file existence, formatting and mechanical checks.
2. **Semantic judges** — research completeness, headline quality, reasoning, article coherence, finance framing and compliance.
3. **Trajectory/eval tests** — verify the runtime actually calls stages in the required order and does not silently degrade.

Passing one class never substitutes for another.

## 10. Promotion rule

v0.2 remains a candidate until all of the following are true:
- unit + trajectory + static audits pass in clean CI on `main`;
- at least one real article completes through all stages;
- expected Word files exist and pass mechanical validation;
- visible audit report is generated;
- final semantic red-team passes;
- resume behavior is exercised at least once on a real task or controlled regression.

Only then should the legacy Drive/Notion control stack be retired or archived.
