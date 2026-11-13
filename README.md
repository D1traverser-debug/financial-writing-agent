# Financial Writing Agent

Financial Writing is a standalone Chinese financial research, editorial and publishing system. It owns its requirements, article state, research methods, writing workflow, reviews, Word production and system evolution.

There is one operating entrypoint: [Financial Writing Skill](skills/financial-writing-agent/SKILL.md). There is no second controller, external parent runtime or parallel task ledger.

## Start and operate

Select the Financial Writing Skill in a fresh ChatGPT session. Use the connected GitHub and research tools available to that session. The Skill directs the complete workflow; this repository is the durable source of truth.

Do not claim that a file was written, a state transition happened or an article was delivered until the GitHub operation has returned and the exact result has been read back. If a required connector or permission is unavailable, continue safe research/editorial work and report the precise blocked operation.

## Active ChatGPT execution path

The active standalone runtime is ChatGPT + the Financial Writing Skill + the user's existing GitHub connector. The plugin is a Skill package; it does not host Python/MCP or grant GitHub permissions. No custom server, local daemon or paid API is required when the GitHub connector is connected with read/write access.

For a single text file, update with its exact current blob SHA and read it back. For atomic multi-file changes, create blobs, create a tree from the current main tree, create a commit parented to the exact current main head, update main with expected_sha and force=false, then fetch every changed file at the resulting commit SHA. Use base64 blobs for DOCX binaries. On a stale-head conflict, reread and recompute; never force or blindly retry. Explicit confirmation in the current conversation authorizes binding requirement changes. The Python adapter is an optional reference implementation and CI test target, not a service that must be deployed for the Skill to operate.

## Canonical file map

| Purpose | Canonical location |
|---|---|
| One operating entry | `skills/financial-writing-agent/SKILL.md` |
| Domain manifest | `config/FINANCIAL_MANIFEST.json` |
| Product and execution contract | `docs/product_requirements.md`, `config/EXECUTION_CONTRACT.json` |
| Data authority and CRUD map | `config/DATA_AUTHORITY.json` |
| Article state | `workspaces/articles/{task_id}/STATE.json` |
| Article research, stages, reviews and delivery | `workspaces/articles/{task_id}/research/`, `stages/`, `reviews/`, `delivery/` |
| Article feedback | `workspaces/articles/{task_id}/feedback/` |
| Reusable methods | `knowledge/METHOD_KNOWLEDGE_CATALOG.json` |
| System evolution and acceptance | `evals/EVOLUTION_INDEX.json`, `evals/quality_regression.json` |
| Python package policy/reference mirror | `financial_writing_agent/resources/` |
| Skill operating reference modules | `skills/financial-writing-agent/references/` |

The per-article `STATE.json` is the only article business-state authority. Research files, stage artifacts, review receipts and deliverables are scoped to that article. The method catalog is the only reusable-method authority. The evolution index is the system-maintenance authority. Chat text, temporary files and external source pages do not become shadow state stores.

## Article production graph

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`.

Research establishes the economic value chain and company universe, checks current primary evidence and counterexamples, and builds the required 15-module PrivateResearchBrief. Editorial creates separate Deep and Broad story blueprints. Drafting produces original prose with claim/source traceability. Review checks factual integrity, originality, reader retention, company grounding, structure, style, compliance and payoff. Delivery creates actual Word files, renders pages, inspects the rendered output and reads back the exact binaries. Failed stages reopen the earliest affected evidence and invalidate dependent downstream receipts.

Normal portfolio outputs are AUDIT_DOCX, FINANCE_DEEP_DOCX, FINANCE_BROAD_DOCX and PLATFORM_INTERACTION_PACK_DOCX, plus PRIVATE_RESEARCH_DOCX when required by the task contract.

A green test suite is engineering evidence, not proof of current financial truth, independent editorial acceptance or reader success.

## Human interaction

Recover the user's complete goal and corrections from available context before asking for more information. Separate hard requirements, corrections, preferences, suggestions, issue reports, questions and approvals. Do not promote a suggestion into a binding requirement. Ask one targeted question only when an unresolved choice materially changes the requested outcome or safe execution. Do not ask the user to choose an implementation when evidence and engineering judgment can resolve it.

A requirement change must be shown as a complete, scoped change before it is written. Preserve prior requirement history and invalidate downstream evidence when its scope changes. Never silently overwrite article history or certify an unreviewed draft.

## Engineering checks

```bash
python -m pip install -e '.[dev]'
coverage run --source=financial_writing_agent -m pytest -q
coverage report -m
python scripts/eval_contracts.py
python scripts/static_audit.py
python scripts/verify_standalone_contract.py
python scripts/whole_tree_audit.py
```

CI also builds and installs an isolated wheel and renders Word products. Engineering PASS remains separate from real article and reader acceptance.
