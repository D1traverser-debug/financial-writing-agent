# Provider-unavailable session draft delivery

## Purpose and activation

Use this route when the hosted Financial Provider Action is unavailable but the user still needs research, analysis, article drafts or Word deliverables. It is the normal session-only route when the active ChatGPT session has the required research and document tools; do not make the user choose between internal implementation options or repeat requirements already available.

This route preserves the Financial content contract while separating content production from canonical task admission and state mutation. No canonical writes occur in this mode. It is not a second task ledger, a free-form shortcut, or evidence that the canonical workflow has completed.

## 1. Recover the goal and establish the session brief

1. Recover the user's current goal, exact deliverables, corrections, constraints, prior decisions and available project context. Consult the Financial Skill, product requirements and accessible prior article files where relevant.
2. For an existing article, read its canonical STATE.json, requirement digest, current artifacts and history as read-only inputs. Never edit, replace, advance or create canonical state in this mode.
3. Write a concise, owner-visible session work brief in the current conversation. Bind the requested outputs, scope, audience, thesis, time horizon, evidence requirements, exclusions, delivery format and unresolved questions.
4. Label the brief SESSION_WORK_BRIEF__NOT_CANONICAL_TASK_INTAKE. It is not a TaskIntakeManifest, has no signed independent intake review and must not be represented as an admitted task.
5. Make reversible assumptions explicit. Ask one focused question only when missing information materially changes the output, authority or risk. Do not ask the user to select a provider implementation or repeat accessible information.

## 2. Execute the Financial content workflow

Use the current Financial-owned research schemas, PrivateResearchBrief requirements, market-explanation and claim-trace rules, story-quality methods, and product requirements. Keep the normal business sequence and evidence boundaries:

- Research current issuer, regulator, filing and other primary sources; preserve source text, retrieval time, body identity, period, units, direction, source family and contradictory evidence.
- Complete the applicable PrivateResearchBrief modules. Separate facts, mechanisms, interpretation, hypotheses and unknowns. Do not turn thematic association into direct company exposure.
- Perform a real Research Audit before drafting. Missing, stale, conflicting or weak evidence stays OPEN and must not be hidden by polished prose.
- Build Deep and Broad as separate products with distinct reader promises, story blueprints, titles, drafts and audits. Broad is not a shortened Deep.
- Produce the platform interaction pack as a separate product when it is included in the requested output contract; do not silently omit or invent outputs.
- Apply all eight PublicationFitness obligations: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF. A material failed gate requires revision or an explicit OPEN/FAIL result; never waive a defect merely to deliver a file.

The model may perform and orchestrate semantic work in the active session. Do not claim that Python callback validators, portfolio_coordinator.run_next_portfolio_stage, owner-stage admission or canonical persistence ran unless they actually ran through their real execution path. A generated pass list, self-declared PASS, hash or CI result is not semantic proof.

## 3. Produce and verify the files

1. Generate only the outputs required by the user's current request and the Financial output contract. Typical products are AUDIT_DOCX, FINANCE_DEEP_DOCX, FINANCE_BROAD_DOCX, PLATFORM_INTERACTION_PACK_DOCX and, when requested, PRIVATE_RESEARCH_DOCX.
2. Save working files in the current execution workspace. Do not place article research, drafts or Word files in the public GitHub repository by default.
3. Reopen each final DOCX from its exact output path, read its actual bytes and compute SHA-256. Bind the delivery-readiness review to those exact bytes, not to an earlier draft, filename, claimed hash or in-memory object.
4. Render the DOCX to page images/PDF and inspect the pages when rendering tools are available. Check missing text, clipping, table overflow, broken page breaks, headers/footers, typography, charts/images and page-level readability. If rendering is unavailable, explicitly leave visual verification OPEN; do not infer it from a successful DOCX save.
5. Check that every requested file exists, is nonempty, opens successfully and is attached to the response. A file path, link, filename or hash alone does not prove that the user can access the artifact.

## 4. Review and report honestly

The active chat may conduct a same-chat content review and report INTERNAL_DELIVERY_READINESS only after the exact session DOCX bytes have been reread and SHA-256-bound. Apply the eight gates to the actual delivered text and identify evidence, location and repair for each material finding.

Same-chat review is not independent editorial acceptance. Keep independent editorial quality and PUBLICATION_CERTIFICATION OPEN. Do not claim a signed independent intake review, signed goal-outcome review, independent reviewer PASS, publication certification, reader acceptance or user acceptance. A draft may be delivered without being certified; its status must remain visible.

Use this exact session completion label only when the files have actually been produced, reread and delivered:

SESSION_DRAFT_DELIVERED__NONCANONICAL__NOT_PUBLICATION_CERTIFIED

If a required tool, source or artifact is unavailable, state the exact limitation and keep the affected proof gate OPEN. Do not report the route as complete when only a plan, prompt, outline or partial file exists.

## 5. Storage and canonical-action boundary

- Deliver completed files as conversation attachments.
- Persist to the user's private Library only when the user explicitly asks for durable private storage.
- Do not create or update workspaces/articles/<task_id>/STATE.json, append canonical receipts, advance stages, change binding requirements, mutate knowledge/METHOD_KNOWLEDGE_CATALOG.json, or close a canonical task.
- Do not use direct GitHub commits, model-generated signatures, synthetic callbacks or ordinary chat confirmation as substitutes for the hosted Provider Action's owner authentication, signed authorization/effect receipts, atomic CAS and exact readback.
- If the user explicitly requests a canonical state or method action, keep that specific action OPEN until the real Provider Action and its required independent evidence are available. Session draft production may continue separately when useful, but it does not satisfy or silently close that canonical action.

The route's only authority is to produce and deliver noncanonical session content. It does not alter the single Financial owner, canonical Article Aggregate, ten-stage business graph, method catalog or independent acceptance requirements.


## 6. Persistent source library

Session Draft Delivery may use the owner-only Google Drive library at ChatGPT / Financial Writing Agent / 00_Source_Library. Its sole registry is Financial Source Registry, with Sources, Versions and Events tabs. Use the connected Drive and Sheets connectors for source-file CRUD and registry read/append operations; do not write source files, private source metadata or task bindings to the public GitHub repository.

For CREATE, search Sources by canonical URL/title and check duplicate IDs. Select the lawful retention policy first. Store user-provided/licensed/public-primary bytes only when permitted; news media default to a permitted short excerpt plus metadata or link-only. Create a source folder and immutable version folder, upload the exact retained payload, then read back the exact Drive file ID, parent folder, MIME type, size, available revision ID, stored bytes and extracted text. Compute SHA-256 over the exact stored payload and retained normalized text. Only then append the Sources row, Versions row and CREATE event; read all three back before treating the source as AVAILABLE.

Use exact references `financial-source://{source_id}/{version_id}`. A version is never overwritten. UPDATE creates a new Drive file ID and appends a Versions row plus ADD_VERSION event. DELETE means RETIRE; RESTORE is explicit. The Events tab is append-only and its row order is lifecycle order. If a multi-step write fails after upload or a registry append, leave the object quarantined/unbound and reconcile it; never silently delete or claim success.

Python helpers are in `financial_writing_agent.source_registry` and `financial_writing_agent.source_readback`. Use `source_records_from_registry_snapshot` to validate the three-tab snapshot and `verify_source_version_readback` / `build_bound_source_reader` to verify file identity, optional revision, MIME type, byte size, raw hash, retained-text hash and source family.

The source registry has no task-binding tab. In session-only mode, keep SourceBindingSet in memory and exact references in the session work brief/deliverables. Do not claim canonical task admission. Canonical bindings remain part of the Article Aggregate and require the hosted Financial Provider Action. Source-library CRUD does not authorize article STATE.json or method-catalog writes.
