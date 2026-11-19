# Financial Writing｜Persistent Source Library

## Canonical location and authority

The canonical source-file store is the owner-only Google Drive folder:

`ChatGPT / Financial Writing Agent / 00_Source_Library`

- `00_Registry / Financial Source Registry`: the only source metadata and lifecycle registry.
- `01_Sources / {source_id} / versions / {version_id}`: immutable source-version objects.
- `99_Retired / {source_id}`: retired source folders retained for history and restoration.

The registry has exactly three tabs: `Sources`, `Versions`, and `Events`. Google Drive owns source identity metadata, source-version metadata, lifecycle history and source payloads. GitHub stores code, rules, schemas, article state and the method catalog. The source library is not a second article ledger.

## Identity and immutable versions

A source ID is `src_<24 lowercase hex>`. A version ID is `vNNNN-<first 12 lowercase hex of the SHA-256 of the exact stored payload>`. A research reference is `financial-source://{source_id}/{version_id}`.

Every accepted version uses a new Drive file ID and is never overwritten. Store the Drive revision ID when the connector exposes it; revision ID is optional because immutable file ID plus exact raw SHA-256 is the required identity. A hash proves byte identity, not factual truth or claim entailment.

## Registry schema

- **Sources**: one row per source identity; title, publisher, canonical URL, source type, scope, task restriction, creation time and source-folder ID.
- **Versions**: one immutable row per version; Drive file/revision IDs, MIME type, byte size, raw payload SHA-256, retained-text SHA-256, source family, publication/retrieval times, storage policy, rights basis, extractor identity and status.
- **Events**: append-only CREATE, ADD_VERSION, RETIRE, RESTORE and BLOCK events. Sheet row order is the event order. Each event records prior/resulting status and version, actor, timestamp, action ID and payload digest when relevant.

Do not add a Bindings or article-state tab. In session-only mode, task bindings remain in memory and in the session work brief. Canonical bindings belong to the Article Aggregate only when the authenticated hosted Provider Action is deployed and the repository privacy gate is satisfied.

## CRUD procedure

### CREATE

1. Search Sources by canonical URL/title and check for duplicate source identity.
2. Mint an opaque source ID; create `01_Sources/{source_id}/versions/{version_id}`.
3. Apply the retention policy before saving content.
4. Upload only the bytes/excerpt/metadata manifest allowed by that policy.
5. Read back the exact Drive file ID, parent folder, MIME type, byte size, optional revision ID, payload bytes and extracted text.
6. Compute SHA-256 over the exact stored payload and the exact retained normalized text. Never hash a URL and call it a document hash.
7. Append one Sources row, one Versions row and one CREATE event row. Read back the rows and Drive object; only then mark AVAILABLE. Otherwise quarantine and do not bind.

### READ and SEARCH

Search the Sources registry by source ID, title, publisher, canonical URL, source type or tags. Resolve the exact version row and fetch by Drive file ID. Verify parent folder, optional revision, MIME type, byte size, raw SHA-256, retained-text SHA-256, source family and retrieval time. Filenames and folder browsing are discovery aids, not identity authority.

### UPDATE

Create a new version folder and a new Drive file ID. Append a Versions row and ADD_VERSION event. Preserve old versions and historical article references. If source content, publication status or a material fact changes, reopen the earliest affected research stage; never silently substitute the latest version into an older article.

### DELETE and RESTORE

Ordinary delete means RETIRE: append a RETIRE event and move the source folder to `99_Retired`. Keep all referenced files, versions and audit events. RESTORE moves the folder back to `01_Sources` and appends a RESTORE event. Physical deletion is limited to disposable unreferenced QA artifacts or explicitly authorized legal erasure.

## Rights and retention

- `RAW_PRESERVED`: only user-provided, licensed or public-primary source material whose retention is lawful.
- `METADATA_AND_EXCERPT_ONLY`: store metadata and only a permitted short excerpt; hash only the excerpt/metadata retained.
- `LINK_ONLY`: store metadata and canonical URL without claiming that source body bytes were preserved.

Public accessibility is not permission to copy an entire copyrighted article. News media default to metadata/excerpt or link-only unless a stronger rights basis exists.

## Research integration and execution boundary

The Python adapter `financial_writing_agent.source_readback.build_bound_source_reader` verifies exact Drive file ID, parent folder, optional revision, MIME type, byte size, raw SHA-256, normalized-text SHA-256 and source family. It adapts the result to `financial_writing_agent.current_research_sources.verify_current_research_sources`.

Direct authenticated Google Drive connector actions provide source-library CRUD in Session Draft Delivery. This does not authorize mutation of article `STATE.json`, article requirements, signed receipts or the reusable-method catalog. Canonical task bindings remain in the Article Aggregate and require the hosted Financial Provider Action. The current repository is public; do not add private article state, private research artifacts, source metadata or task bindings to it.

## Current provisioned state

The Drive root and owner-only permissions have been read back. The Financial Source Registry has the three required tabs and exact headers. Disposable integration fixtures verified file creation, exact DOCX upload/readback and hashes, immutable v1/v2 file IDs, registry append/read, and retire/restore moves; QA fixtures were removed. Production Sources, Versions and Events rows remain empty until actual research sources are ingested.
