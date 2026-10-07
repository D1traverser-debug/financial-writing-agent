# Financial Writing Agent v0.2.1 candidate

A deterministic A-share financial-writing runtime for research-heavy formal articles and image-first WeChat sticker posts.

## Current truth
- Repository: `D1traverser-debug/financial-writing-agent`
- Stable branch: `main`
- Current hardening branch: `v0.2.1-runtime-rule-hardening`
- Python package: `financial_writing_agent`
- CLI: `financial-write` (developer diagnostic path)
- Production interaction surface: typed MCP plugin + packaged `financial-writing-agent` Skill
- **User-authorized real article live-model E2E passed: 0**

A fixture, unit/trajectory test, mock article, manually inspected draft, or a run that never returned/downloaded and validated its final Word artifacts does **not** count as a real E2E.

## Runtime
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Failures or unavailable mandatory dependencies route to `BLOCKED`; there is no silent free-form fallback. Revision routes target the earliest valid repair stage and invalidate stale downstream gates/artifacts.

## Control-plane design
The model owns judgment-heavy work: research synthesis, TopicDNA, independent mode structures, headlines, prose, semantic/style audits and visual planning/generation.

The Python/MCP harness owns what should not rely on model memory:
- legal stage transitions and checkpoint persistence;
- mandatory gate inventory;
- strict Pydantic stage contracts;
- evidence verification status/source-group receipts;
- DUAL mode-specific editorial plans;
- frozen `WritingAcceptanceContract` before drafting;
- criterion-level final acceptance evidence;
- revision invalidation propagation;
- required artifact identity/readback/checksum;
- Word construction and mechanical QA;
- rendered-page resource inventory;
- completion authority.

## Core behavior
- Unspecified formal-article destination → `DUAL`.
- `DUAL` = one broad/deep research base + independently structured/edited `FINANCE_DEEP` and `FINANCE_BROAD` articles.
- Each applicable mode generates 2–3 candidate structures and selects independently after shared TopicDNA.
- Default formal language = Simplified Chinese financial prose.
- Default formal delivery = `WORD_FILE_ONLY`.
- New Word articles use the current integrated visual workflow unless explicitly disabled or the task concerns an existing document.
- Formal hierarchy is normalized to `一、二、三 → （1）（2）（3） → ①②③`.
- Formal articles require one independent lead before the first H1.
- A dedicated anti-AI/style judge must pass before general editorial audit can pass.
- Public financial output requires a concise but materially complete risk warning/disclaimer.
- Completion returns Word artifact(s), `WRITING_AUDIT_REPORT.docx`, visual manifest when applicable, and a visible completion checklist.

## Research/evidence contract
Research is deliberately broader/deeper than the article. It covers catalyst, concept map, industry chain, A-share universe, fundamentals, why-this/why-not, market selection, counterevidence and relevant short-term roles/signals.

Evidence explicitly distinguishes:
- `UNRESOLVED`;
- `SINGLE_SOURCE_ATTRIBUTED` with allowed wording;
- `INDEPENDENTLY_CROSS_CHECKED` with genuinely independent source groups.

Core title/lead/H1/conclusion claims cannot be backed by unresolved evidence. Writing keeps StockBase read-only; stable corrections go to the run ReviewQueue.

## Acceptance/final audit
Selected titles and mode-specific structures freeze a `WritingAcceptanceContract` before DRAFT. The draft must match the frozen title and exact H1 sequence.

FINAL PASS requires machine-checked `KEY: concrete evidence` coverage for every applicable criterion (title, lead, H1 structure, side focus, company-selection basis, headline anchor, opening payoff, reasoning continuity, compliance/risk, DUAL cross-version consistency and visual alignment where applicable), plus global evidence/output checks.

The engine also refuses COMPLETE if any mandatory gate is absent, not only when an existing gate is FAIL/REVISE/NOT_RUN.

## Visual/Word delivery
Creative generation stays model-side. Runtime accepts a validated `VisualPackage`, records `VISUAL_MANIFEST.json`, and deterministically inserts assets into Word. Formal article defaults: 16:9 hero + semantic section images at roughly one per 700 Chinese characters, centered and uncropped.

File ingestion validates public HTTPS targets including redirect destinations. Word mechanical QA checks hierarchy/style, H1 numbering/color/bold/size, H2/H3 style/sequence, stock-name bold spans across Word runs, Markdown leakage, underlines, abnormal empty paragraphs, compliance red-line phrases, risk section and image count.

Successful DOCX rendering is **not** visual page QA. The MCP surface exposes every rendered page as `writing-render://...`; FINAL must inspect every returned page and provide the exact reviewed resource URI set before PASS.

## MCP surface
The hosted/plugin-facing runtime exposes 15 typed tools plus artifact/render resources. Public summaries never expose server-local artifact paths.

## Agents SDK diagnostics
The optional standalone Agents SDK path exists for developer diagnostics, not as a substitute for the production MCP/ChatGPT visual workflow. Stage calls use structured outputs and task-grouped tracing metadata with sensitive trace content disabled. CI includes an SDK structural smoke and a deterministic `ScriptedModel` orchestration test.

## Deployment boundary
The included SQLite state store and local run directory are reference/local-CI implementations. A hosted production deployment still requires verified durable state and persistent artifact/object storage that survive runtime restart and fresh ChatGPT sessions. Do not claim production readiness while state/artifacts depend on ephemeral local disk.

## Validation policy
Clean CI must pass SDK smoke, MCP HTTP smoke, unit/trajectory/harness tests, executable contract evals, static ownership/reference audit, wheel-isolated install smoke and real DOCX render smoke.

v0.2.1 remains a **candidate** until a user-authorized real article live-model E2E:
1. starts from a fresh chat;
2. uses real research/model stages and real generated visuals where applicable;
3. deliberately interrupts mid-run;
4. resumes from the durable checkpoint without repeating passed stages/user input;
5. returns the actual final Word artifact(s) + `WRITING_AUDIT_REPORT.docx`;
6. inspects every rendered Word page;
7. re-reads artifact identity/checksums;
8. proves the same unfinished/completed task survives runtime restart/fresh-chat recovery.
