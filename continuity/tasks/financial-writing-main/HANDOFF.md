# 金融文章写作｜Continuity Handoff

- task_id: `financial-writing:main`
- display_name_zh: **金融文章写作**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: FINANCIAL_WRITING_AGENT_RUNTIME
- current_stage: `SYSTEM_HARDENING_REGRESSION`
- continuity_contract: `CONTINUITY_V3_7`
- writing_contract: `Financial Writing Agent v0.6`
- writing_rule_authority: `D1traverser-debug/financial-writing-agent@main`

## Exact next action
Finish the current v0.6 system-level regression against the final `main` HEAD. Treat CI/static/eval failures as implementation or contract defects and repair the owning layer; do not duplicate the rule in prompts. When the final HEAD is fully green, return this workspace to `READY_FOR_NEW_OR_EXPLICIT_ARTICLE`.

## Runtime compatibility boundary
- Current repository runtime is v0.6 standalone/reference runtime.
- No Financial Writing Site Runtime plugin is currently installed.
- Any future Site must implement the current v0.6 contract directly and pass the v0.6 promotion checks before use.
- Repository capability declarations are not proof that a particular chat/session has the required executor; use `continuity/EXECUTION_CAPABILITIES.json` for per-stage capability handshake.

## Legacy boundary
Do not restore old Site PoC contracts, `mcp_server.py`, `CHAT_TEXT`, visual/sticker resources, canned `structure_patterns.md`, v0.4/v0.5 headline/style payloads, blanket company-name bolding, or the old company-universe-implies-market-explanation rule.

## Continuity status
This handoff has been reconciled from the old v3.3 format to Universal Continuity v3.7 in the same active writer lease. `resume_epoch` and active lease remain unchanged in `TASK_MANIFEST.json`.

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

The handoff intentionally does not duplicate the full writing rubric; canonical rules live in the references above.
