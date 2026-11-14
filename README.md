# Financial Writing Agent

Financial Writing is a standalone Chinese financial research, editorial and publishing system. It owns its requirements, article state, research methods, writing workflow, reviews, Word production and system evolution.

There is one operating entrypoint: [Financial Writing Skill](skills/financial-writing-agent/SKILL.md). There is no second controller, external parent runtime or parallel task ledger.

## Start and operate

Select the Financial Writing Skill in a fresh ChatGPT session. Use the connected GitHub and research tools available to that session. The Skill directs the complete workflow; this repository is the durable source of truth.

Do not claim that a file was written, a state transition happened or an article was delivered until the GitHub operation has returned and the exact result has been read back. If a required connector or permission is unavailable, continue safe research/editorial work and report the precise blocked operation.

## Active ChatGPT execution path

The native client is ChatGPT following the Financial Writing Skill with the user's connected GitHub provider. This client can recover the current article, research, draft, evaluate candidate alternatives, and persist candidate work on a non-authoritative branch. The Skill plugin cannot run Python or independently authenticate owner approval; the GitHub connector grants transport, not business action authorization. No CAOS parent, second controller or duplicated task ledger is required.

**Business-state effects are a separate execution boundary.** Article `STATE.json`, bound stage artifacts and `knowledge/METHOD_KNOWLEDGE_CATALOG.json` may be changed only by the authenticated `financial_writing_agent.standalone_runtime` action port or a candidate PR that passes the exact parent/head two-revision owner-effect audit implemented in `financial_writing_agent.whole_system_assurance` and called from `scripts/system_acceptance_report.py` in CI. No direct ChatGPT `update_file` or blob/tree/commit `update_ref` to `main` counts as legal owner admission. GitHub CAS plus exact readback prove the bytes written, not the semantic authorization. A binding requirement change additionally requires the complete original user message, normalized change, explicit owner confirmation and genuine external signed proof; model-generated signatures and same-session self-review are invalid.

For a safe candidate change: read the exact `main` SHA and file identities, create/update the candidate branch with expected-SHA no-force writes, run the full current-source CI and two-revision owner-effect review, merge only a legitimate verified candidate, and read back the actual resulting production bytes. For DOCX artifacts, base64 Git blobs and exact binary readback are required. A stale SHA or uncertain remote result must be reconciled; never blindly retry. If the real Python admission/signer is unavailable in a Skill-only chat, preserve the proposed action as OPEN and continue independent lawful research/drafting; never silently fake authority or certify a completed article.

See [Financial standalone interface](docs/STANDALONE_INTERFACE.md) and [whole-chain governance and falsification](docs/FINANCIAL_WHOLE_CONTROL_CHAIN_DECISION_20261114.md) for evidence boundaries.

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

## Authenticated article effects

New article mutations require both a signed request authorization and a separately signed effect receipt bound to the exact resulting STATE.json Git blob. The state and actions/<action_id>.effect.json receipt are written in one atomic CAS commit and independently read back. Historical signed v1.0 receipts remain explicitly effect-unbound; new writes use authorization v1.1 plus effect receipt v1.0. The live authenticated provider remains an external acceptance gate; synthetic CI does not certify it.
