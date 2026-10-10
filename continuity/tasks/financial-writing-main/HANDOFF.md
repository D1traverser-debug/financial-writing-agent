# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: FINANCIAL_WRITING_AGENT_RUNTIME
- current_stage: `READY_FOR_NEW_OR_EXPLICIT_ARTICLE`
- continuity_contract: `CONTINUITY_V3_7`
- writing_contract: `Financial Writing Agent v0.6`
- writing_rule_authority: `D1traverser-debug/financial-writing-agent@main`

## Validated system state
The v0.6 system-level regression is complete. Validated business-code HEAD: `484a706c2b37bb61d338f3aa09d66041649ae404`. GitHub Actions run `38017887418` completed successfully with SDK smoke, 17-tool MCP smoke, unit/trajectory tests, executable contract evals, static authority/version audit, isolated wheel install and DOCX render smoke all PASS.

## Exact next action
Accept the user's next financial-article topic/source and start the current v0.6 workflow. Research must explicitly classify `market_explanation_scope` as `REQUIRED` or `NOT_MATERIAL`; then apply the current Reader Funnel, Natural Authorial Prose / Writing DNA, general editorial, Word mechanical and final-audit contracts. Do not revive any removed compatibility path.

## Runtime compatibility boundary
- Current repository runtime is the validated v0.6 standalone/reference runtime.
- No Financial Writing Site Runtime plugin is currently installed.
- Any future Site must implement the current v0.6 contract directly and pass the v0.6 promotion checks before use.
- Repository capability declarations are not proof that a particular chat/session has the required executor; use `continuity/EXECUTION_CAPABILITIES.json` for per-stage capability handshake.

## Legacy boundary
Do not restore old Site PoC contracts, `mcp_server.py`, `CHAT_TEXT`, visual/sticker resources, canned `structure_patterns.md`, v0.4/v0.5 headline/style payloads, blanket company-name bolding, the old company-universe-implies-market-explanation rule, or obsolete Human Voice naming/contracts.

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
