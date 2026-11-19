# Financial Writing — Data Authority and Source File Lifecycle Decision

**Date:** 2026-11-19  
**Status:** Architecture candidate; source CRUD remains blocked pending privacy and provider gates.  
**Scope:** Financial Writing repository, canonical business data, and source-file CRUD only.

## 1. Decision summary

The Financial Writing system needs one durable source-file authority. The current repository is already the declared owner of article state, method knowledge, and task artifacts. The least disruptive first step is to preserve that history and make the existing canonical repository private before it stores or accepts any additional business data.

The source library will live at the repository root under `sources/`. It will be a global, versioned source library. Article workspaces will store exact references to immutable source versions, not duplicate source originals.

A second data repository is not introduced in this phase. Splitting the existing state, method catalog, and source history across repositories before the provider and migration protocol exist would create multiple authorities and require cross-repository CAS, authorization, and recovery semantics. If public code distribution is later required, create a sanitized code-only mirror after private-data isolation; do not keep private business artifacts in a public code repository.

## 2. Verified current-state findings

At the audit point:

- `D1traverser-debug/financial-writing-agent` is public.
- `main` is `1f6745a39412c8adbbd7e1d5cbd05cae1d6ef4dc`.
- The tracked tree contains seven article task workspaces and 128 workspace paths.
- Those workspaces include private-research briefs, company-universe data, article stages, audit records, feedback, and task state.
- `config/DATA_AUTHORITY.json` declares this same repository as the single business authority but does not define a global source-file store.
- `financial_writing_agent/current_research_sources.py` verifies provider-returned source bytes, hashes, source families, and freshness. It does not create, store, version, list, update, retire, or delete source files.
- `financial_writing_agent/resources.py` reads packaged policy resources; it is not a business-file manager.
- `financial_writing_agent/artifact_hygiene.py` validates task-artifact lifecycle labels; it is not source-file CRUD.
- The current source reader is an injected callback. The hosted Financial Provider Action is not deployed, so canonical owner-state, method, and source mutations are not available through the current Skill-only session.
- No active `sources/` root or dedicated Financial Writing folder was found in the connected Library/Drive locations inspected for this audit.

These findings mean the previous claim that Financial already had complete source-file CRUD was incorrect. Existing source verification and article-artifact storage do not amount to source-file management.

## 3. Immediate security gate

The current repository is public while containing business and research artifacts described by the system as private. This is an existing data-isolation failure, not a future design concern.

Required action before any new source original, private research artifact, or canonical business record is written:

1. Change the existing repository visibility to **Private**.
2. Preserve its existing Git history; do not delete or rewrite historical data as a shortcut.
3. Verify the repository metadata reports Private.
4. Verify the hosted Financial Provider Action has least-privilege access to this private repository and can perform exact readback.

The connected GitHub actions available in this session do not expose a repository-visibility mutation. No visibility change has been attempted. Until the owner completes and verifies this gate, source CRUD remains blocked and no new business files may be added to the repository.

If the owner requires the code to remain public, that is a separate later migration: create a sanitized public code-only mirror and keep the existing canonical repository private. Do not solve this by moving only current files while leaving their history publicly reachable.

## 4. Canonical source-library location

The single canonical location is:

```text
sources/
  {source_id}/
    SOURCE.json
    versions/
      {version_id}/
        MANIFEST.json
        original.{safe_extension}
        normalized.txt
    actions/
      {action_id}.effect.json

workspaces/
  articles/
    {task_id}/
      research/
        SOURCE_BINDINGS.json
        EVIDENCE_LEDGER.json
        PRIVATE_RESEARCH_BRIEF.json
```

The global `sources/` library owns source identity, versions, provenance, and lifecycle. The article's `SOURCE_BINDINGS.json` owns only the exact source versions used by that task. The evidence ledger owns claim-to-source/claim-to-passage relationships. These are distinct objects, not duplicate source registries.

Canonical reference format:

`financial-source://{source_id}/{version_id}`

A task must pin an exact version. A floating "latest" reference is forbidden in admitted research because a later source update must not silently change old article evidence.

## 5. Source-file lifecycle

| Operation | Required behavior |
|---|---|
| Create | Create a stable source identity, immutable first version, provenance manifest, and signed effect receipt in one conditional Git commit; read back all exact blobs. |
| Read | Resolve exact source ID and version; verify original bytes, normalized text, manifest, and Git blob identities. |
| Update | Append a new immutable version and CAS-update the source's current-version pointer. Never overwrite an admitted version. |
| Delete | Default to RETIRE. Retired sources cannot be newly bound, but existing article references and historical evidence remain readable. RESTORE is explicit. |
| Hard delete | Forbidden for any source referenced by a task, evidence ledger, receipt, or audit. Legal erasure requires a separate approved history/backup purge process. |
| List/search | Query source metadata and return exact version-pinned references, never filename-only matches. |

Every version records at least the original-byte SHA-256, normalized-text SHA-256, Git blob SHA for each stored file, source family, source type, publisher, canonical URL, publication/retrieval times, media type, extraction tool/version, storage/rights policy, and source scope.

## 6. Provider and verification boundary

The current `verify_current_research_sources` function remains a verifier, not a source manager. The missing layer is a trusted source resolver and lifecycle provider.

Required provider surface:

- `list_sources` — metadata search and listing.
- `observe_source` — read source identity, current version, status, and action history.
- `read_source_version` — retrieve one exact immutable version and verify bytes.
- `admit_source_action` — authenticated CREATE, ADD_VERSION, RETIRE, or RESTORE.

Mutations require authenticated owner identity, exact action digest, provider-signed authorization/effect receipts, expected-SHA CAS, atomic source-record/effect commit, exact readback, and idempotent timeout reconciliation. The model must not bypass this path with direct GitHub commits.

## 7. Rights, scope, and retention

- User-provided files may be preserved as original bytes in the private store, subject to user intent and applicable restrictions.
- Public primary documents may be retained when lawful and within provider limits.
- News/paywalled material must not be copied in full by default. Keep the URL, bibliographic metadata, permitted short excerpts, and retrieval/body digests unless the user has rights or a license.
- Oversized files must fail closed until an approved object-storage provider exists. Do not silently fall back to a public repository, temporary workspace, Library, or Drive as a second canonical store.
- Sources may be marked task-only or reusable. Cross-task reuse requires the source scope to allow it.
- Private originals and research artifacts are never publication outputs unless explicitly authorized.

## 8. Existing history and migration

No historical article state, receipt, accepted evidence, or source artifact is moved, rewritten, or deleted by this decision.

After the privacy gate and provider deployment:

1. Inventory existing source references in each active task.
2. Classify each reference as an original file, primary URL, secondary/news URL, dataset, or unsupported/unresolvable reference.
3. Ingest only sources that can be lawfully preserved and whose exact provenance can be established.
4. Create task-specific source bindings for new/current work; do not retroactively claim old tasks used the new source library.
5. Preserve unresolved legacy references as historical provenance and mark them non-current where freshness cannot be re-established.

## 9. Acceptance gates

The source library is not production-ready until all are true:

- The canonical repository is verified Private.
- The live provider is deployed and installed with least privilege.
- Source CRUD actions have exact owner authorization, signed effects, atomic CAS, and exact readback.
- Positive and negative tests cover create/read/version update/retire/restore/list, stale SHA, replay, wrong actor, altered bytes, cross-task scope, and timeout-after-commit.
- A real source file is ingested, reread by exact version, bound to one article, and independently checked.
- No source original or private research artifact is written to a public repository.

**Current result:** architecture decision prepared; privacy gate OPEN; source CRUD NOT_IMPLEMENTED; provider NOT_DEPLOYED.