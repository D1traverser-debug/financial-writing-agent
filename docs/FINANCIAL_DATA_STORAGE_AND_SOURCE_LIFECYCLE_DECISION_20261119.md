# Financial Writing — Data Authority and Source File Lifecycle Decision

**Date:** 2026-11-19  
**Status:** Architecture candidate; Drive folder provisioned; source CRUD adapter not implemented.  
**Scope:** Financial Writing data authority, raw-source storage, source-file CRUD, and task-source binding.

## 1. Decision summary

Use a two-plane storage design with distinct object ownership:

- **GitHub Financial Writing repository:** owns code, rules, schemas, article state, source identity/lifecycle metadata, exact task-source bindings, and signed effect receipts.
- **Google Drive:** owns original binary source files, immutable source-version objects, and large raw materials.
- **Notion:** may provide reusable research knowledge and evidence-link notes, but is not the raw-source file authority.
- **ChatGPT Library:** continuity/navigation and historical attachments only; not the raw-source authority.

This is not two competing business-state ledgers. Drive owns file bytes; GitHub owns the source identity/version mapping and article business state. Every article binds an exact Drive file ID, Drive revision ID, and SHA-256 through the GitHub task state.

## 2. Verified current-state findings

At the audit point:

- `D1traverser-debug/financial-writing-agent` is Public.
- `main` is `1f6745a39412c8adbbd7e1d5cbd05cae1d6ef4dc`.
- The tracked tree contains seven article task workspaces and 128 workspace paths.
- Those workspaces include private-research briefs, company-universe data, article stages, audit records, feedback, and task state.
- `config/DATA_AUTHORITY.json` declares this repository as the business authority but does not define a raw-source file store.
- `financial_writing_agent/current_research_sources.py` verifies provider-returned source bytes, hashes, source families, and freshness. It does not create, store, version, list, update, retire, or delete source files.
- `financial_writing_agent/resources.py` reads packaged policy resources; it is not a business-file manager.
- `financial_writing_agent/artifact_hygiene.py` validates task-artifact lifecycle labels; it is not source-file CRUD.
- The current source reader is an injected callback. The hosted Financial Provider Action is not deployed, so canonical owner-state, method, and source mutations are not available through the current Skill-only session.
- The active cross-conversation handoff separates storage roles: GitHub owns engineering truth and domain execution entry; Google Drive stores raw materials and large files; Notion is knowledge navigation/review; Library is continuity/navigation.
- The handoff explicitly excludes news-reading scripts and Word document merging from Financial Writing. Such files must never be auto-imported as article sources.
- No dedicated Financial Writing source folder existed in the inspected Drive tree. A new private folder has now been provisioned and permission-checked.

## 3. Exact source-library location

The private Google Drive location is:

```text
ChatGPT/
  Financial Writing Agent/
    00_Source_Library/
      {source_id}/
        versions/
          {version_id}/
            original.{safe_extension}
            MANIFEST.json
```

Drive folder:
- Project folder ID is held in private provider configuration.
- Source library folder ID is held in private provider configuration.
- The parent and source folders were read back as `shared=false`, with owner-only permission metadata.

The folder is currently empty. No historical documents or unrelated attachments were moved into it.

## 4. Canonical metadata and task-binding locations

The GitHub repository remains the authority for source identity and lifecycle metadata:

`sources/{source_id}/SOURCE.json`

Immutable provider effect records:

`sources/{source_id}/actions/{action_id}.effect.json`

Each article binds exact source versions at:

`workspaces/articles/{task_id}/research/SOURCE_BINDINGS.json`

The GitHub source record maps `source_id/version_id` to:
- exact Drive folder ID;
- exact Drive file ID;
- exact Drive revision ID;
- raw-byte SHA-256;
- normalized-text SHA-256;
- source family/type, publisher, URL, published/retrieved timestamps;
- media type, size, storage/rights policy, and extraction tool/version.

Canonical source reference:

`financial-source://{source_id}/{version_id}`

A task must pin an exact version. A floating `latest` reference is forbidden in admitted research.

## 5. Source-file lifecycle

| Operation | Required behavior |
|---|---|
| Create | Upload a new immutable original to the private Drive folder; fetch/read back the exact file/revision; compute SHA-256; then commit the GitHub source record and signed effect receipt atomically with expected-SHA CAS and exact readback. |
| Read | Resolve the exact source/version through GitHub metadata; read the exact Drive file/revision; verify raw bytes, normalized text, and metadata digests. |
| Update | Upload a new Drive file for the new version. Never overwrite an admitted version. After Drive readback, CAS-update the GitHub source record and append the signed effect receipt. |
| Delete | Default to RETIRE in the GitHub source record. Prevent new task bindings but preserve Drive originals and historical article references. RESTORE is explicit. |
| Hard delete | Forbidden for any source referenced by an article, evidence ledger, receipt, or audit. Legal erasure requires a separately approved history/backup purge. |
| List/search | Search the GitHub source registry by metadata; return exact source/version references. Drive folder listing is an object-store operation, not the business registry. |

### Two-phase write and recovery

Drive upload and GitHub metadata commit are separate systems; they cannot be one atomic transaction.

1. Upload the immutable Drive object.
2. Read back its exact file ID/revision and bytes; recompute SHA-256.
3. Only then admit the GitHub source record/effect receipt using expected-SHA CAS.
4. If Drive upload succeeds but GitHub commit fails, leave an unreferenced object for reconciliation; do not silently delete it.
5. If GitHub metadata exists but Drive bytes are missing or changed, fail closed and block source use.
6. Timeouts are unknown outcomes until exact Drive and GitHub readback reconciles them.

## 6. Provider and verification boundary

The current `verify_current_research_sources` function remains a verifier, not a source manager. The missing layer is a trusted Drive source resolver and lifecycle adapter.

Required provider surface:

- `list_sources` — metadata search and listing.
- `observe_source` — read source identity, current version, status, and action history.
- `read_source_version` — retrieve one exact immutable Drive version and verify bytes.
- `admit_source_action` — authenticated CREATE, ADD_VERSION, RETIRE, or RESTORE.

The hosted Financial Provider Action must have:
- least-privilege Google Drive access limited to the source-library folder;
- least-privilege GitHub App access to the Financial repository;
- owner authentication and exact action-digest confirmation;
- signed authorization/effect receipts;
- GitHub expected-SHA CAS for source metadata and task-state bindings;
- exact Drive file/revision byte readback and exact GitHub blob readback.

The Drive folder exists, but this provider integration is NOT_DEPLOYED. Direct connector operations can inspect and stage files, but must not be represented as canonical Financial source admission until the trusted adapter is implemented and tested.

## 7. Input boundary and other knowledge systems

- Only files explicitly supplied for the current Financial task or sources deliberately acquired during its current research may be ingested.
- A normal new article is NEW_TASK. It does not inherit recent conversation attachments, old task artifacts, or unrelated Library files.
- Only explicit continuation may read the named article STATE and its exact source bindings.
- News-reading scripts and Word-document merge inputs are a separate file-processing workflow. They are not Financial Writing inputs and must not be auto-ingested.
- Notion IndustryBase/EventBase/ArticleBase/EvidenceCache pages are reusable knowledge and evidence-link notes, not original source bytes. Revalidate their facts and source dates before use.
- ChatGPT Library old recovery entries and historical attachments are not source authority.
- Public primary documents may be preserved when lawful. News/paywalled material must not be copied in full by default; retain URL, metadata, permitted short excerpts, and retrieval/body digests unless rights or license permit full storage.

## 8. Immediate security gate

The current GitHub repository is Public while containing article workspaces and research artifacts described as private. This is an existing data-isolation failure.

Before writing new private source metadata, task bindings, or research artifacts to GitHub:

1. Change the existing repository visibility to **Private**.
2. Preserve existing Git history; do not delete or rewrite historical data as a shortcut.
3. Verify repository metadata reports Private.
4. Verify the hosted Provider Action has least-privilege access to the private repository and the Drive source folder.

The connected GitHub actions available in this session do not expose a repository-visibility mutation. No visibility change has been attempted. If the owner requires public code distribution, create a sanitized public code-only mirror later; do not leave private task history in the public repository.

## 9. Existing history and migration

No historical article state, receipt, accepted evidence, or source artifact is moved, rewritten, or deleted by this decision.

After the privacy gate and provider deployment:

1. Inventory existing source references in each active task.
2. Classify each as user-supplied original, public primary document, secondary/news URL, dataset, or unsupported/unresolvable reference.
3. Ingest only sources that can be lawfully preserved and whose exact provenance can be established.
4. Create task-specific source bindings for new/current work; do not retroactively claim old tasks used the new source library.
5. Preserve unresolved legacy references as historical provenance and mark them non-current where freshness cannot be re-established.

## 10. Acceptance gates

The source library is not production-ready until all are true:

- The canonical Financial GitHub repository is verified Private.
- The Google Drive source folder is verified Private.
- The hosted Provider Action is deployed with least-privilege Drive and GitHub access.
- Source CRUD actions have exact owner authorization, signed effects, GitHub CAS, exact Drive byte readback, and exact GitHub readback.
- Positive and negative tests cover create/read/version update/retire/restore/list, stale SHA, replay, wrong actor, altered bytes, Drive revision mismatch, cross-task scope, and timeout reconciliation.
- A real source file is ingested, reread by exact Drive file/revision, bound to one article, and independently checked.

**Current result:** private Drive source folder provisioned and verified; no source file ingested; deterministic source models/transitions implemented; Drive/GitHub source CRUD provider NOT_DEPLOYED; GitHub privacy gate OPEN.