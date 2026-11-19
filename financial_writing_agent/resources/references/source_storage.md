# Financial Writing — Source File Storage and Intake Rules

**Status:** The private Drive folder is provisioned. Canonical source CRUD is not active until the GitHub repository is Private and the hosted Financial Provider Action has a working Drive adapter.

## Storage ownership

- Raw original bytes and immutable version files: Google Drive folder `ChatGPT/Financial Writing Agent/00_Source_Library`.
- Source identity, lifecycle metadata, and signed source-action effects: GitHub `sources/{source_id}/SOURCE.json` and `sources/{source_id}/actions/{action_id}.effect.json`.
- Exact article source bindings: GitHub `workspaces/articles/{task_id}/research/SOURCE_BINDINGS.json`.
- Canonical reference: `financial-source://{source_id}/{version_id}`; each binding resolves to an exact Drive file ID, revision ID, and SHA-256.

## CRUD rules

- **Create:** upload a new Drive file, read back the exact file/revision and bytes, compute SHA-256, then admit the GitHub source record and signed effect receipt through provider CAS/readback.
- **Read:** resolve by source ID and version ID, not filename; verify Drive revision, raw SHA-256, normalized-text SHA-256, and provenance.
- **Update:** create a new Drive file/version. Never overwrite an admitted version. CAS-update the GitHub source record only after exact Drive readback.
- **Delete:** RETIRE by default. Preserve old Drive versions and existing article bindings. Hard deletion of referenced sources is forbidden.
- **List/search:** search the GitHub source registry by metadata; Drive folder listing is object discovery, not the source business registry.

## Intake boundary

Ingest only files explicitly supplied for the current Financial task or sources deliberately acquired during its research. A new article is a NEW_TASK and does not inherit unrelated recent attachments or historical Library files. Only explicit continuation may restore a named article STATE and its exact source bindings.

News-reading scripts and Word-document merge inputs are separate workflows, not Financial Writing sources. Notion IndustryBase/EventBase/ArticleBase/EvidenceCache pages are reusable knowledge or evidence-link notes, not original source bytes. ChatGPT Library is continuity/navigation, not raw-source storage.

## Safety gates

- The GitHub Financial repository is currently Public and contains private-research artifacts. Do not write new private source metadata, task bindings, or research artifacts until its visibility is verified Private. Preserve existing history.
- The Drive source folder was read back as not shared and owner-only. Keep it private.
- The hosted provider must have least-privilege Drive access to this folder and GitHub App access to the Financial repository. It must verify exact Drive bytes before committing GitHub metadata/effect.
- The provider and source CRUD adapter are NOT_DEPLOYED. Do not claim durable source admission or production CRUD yet.
