# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: FINANCIAL_WRITING_AGENT_RUNTIME
- current_stage: `READY_FOR_NEW_OR_EXPLICIT_ARTICLE`
- continuity_contract: `CONTINUITY_V3_7`
- writing_contract: `Financial Writing Agent v0.7`
- writing_rule_authority: `D1traverser-debug/financial-writing-agent@main`

## Validated system state
The v0.7 system-level regression is complete. Validated business-code HEAD: `44b78e7895c0e912699033a0be56da67efea25cf`. GitHub Actions run `38029561987` completed successfully with SDK smoke, 17-tool MCP smoke, **49 unit/trajectory tests**, executable contract evals, static authority/version audit, isolated wheel install and DOCX render smoke all PASS.

v0.7 hardens the failures exposed by the offshore-wind draft: class-accounted Universe Coverage, at-least-two materially different recall sources, `MATERIAL / SECONDARY / REFERENCE_ONLY` company classification, Deep MATERIAL-company reconciliation, stock-grounded monitoring/validation sections, conditional numbered Deep navigation, title pools spanning at least five real angle families, deterministic template-cluster guards, and independent semantic-audit provenance. A chat self-review cannot certify semantic PASS.

## Exact next action
Accept the user's next financial-article topic/source or explicit rewrite request and start the current v0.7 workflow. For company/theme work, build the Universe Coverage Ledger before narrowing; FINANCE_DEEP must discharge every MATERIAL company obligation and may not substitute a few representative stocks for completeness. Monitoring/validation/falsification sections must map signals back to named stocks or explicit value-chain classes. Titles must be strategy-diverse rather than synonym variants. Do not revive any removed compatibility path.

## Runtime compatibility boundary
- Current repository runtime is the validated v0.7 standalone/reference runtime.
- No Financial Writing Site Runtime plugin is currently installed.
- Any future Site must implement the current v0.7 contract directly and pass the v0.7 promotion checks before use.
- Repository capability declarations are not proof that a particular chat/session has the required executor; use `continuity/EXECUTION_CAPABILITIES.json` for per-stage capability handshake.

## External knowledge boundary
- GitHub `main` is the only Financial Writing code/rule authority.
- Google Drive and Notion may provide read-only research knowledge, StockBase/ArticleBase evidence or historical traces, but may not restore an older writing controller, QA gate, CURRENT_RUN or task pointer over the GitHub contract.
- Old Drive writing-controller/QA surfaces have been explicitly decommissioned or downgraded to LEGACY/MIRROR; Notion's old `CURRENT_CHAT_HANDOFF` is marked deprecated.
- Valuable StockBase/ArticleBase/history evidence is retained as knowledge rather than destroyed; retention does not grant execution authority.

## Legacy boundary
Do not restore old Site PoC contracts, `mcp_server.py`, `CHAT_TEXT`, visual/sticker resources, canned `structure_patterns.md`, v0.4/v0.5/v0.6 headline/style payloads, blanket company-name bolding, the old company-universe-implies-market-explanation rule, obsolete Human Voice naming/contracts, representative-stock Deep shortcuts, synonym-only headline pools or author self-certified semantic PASS.

## Continuity status
This handoff is reconciled to Universal Continuity v3.7. `resume_epoch` and the active lease remain unchanged in `TASK_MANIFEST.json` because this was a same-writer system hardening cycle, not a takeover.

## Authority refs
- `skills/financial-writing-agent/SKILL.md`
- `config/policy.json`
- `config/rule_ownership.json`
- `references/research.md`
- `references/market_explanation.md`
- `references/hooks.md`
- `references/editorial.md`
- `references/style.md`
- `references/delivery.md`
- `references/audit.md`
- `references/maintenance.md`
- `docs/architecture.md`
- `deploy/chatgpt-site/SITE_SPEC.md`
- `continuity/EXECUTION_CAPABILITIES.json`

The handoff intentionally does not duplicate the full writing rubric; canonical rules live in the authority refs above.
