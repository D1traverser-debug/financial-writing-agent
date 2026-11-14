# Method-catalog effect binding and replay repair — 2026-11-14

## Status

Candidate implementation in progress on financial/method-catalog-effect-binding-20261114. Baseline main: 0cabd473f4d9adaf687121a66f8f5701dfe606a2. This record does not claim merge or live provider acceptance.

## Reconstructed goal

The Financial method catalog is an owner-governed business authority. A method mutation must prove the exact prior catalog, the exact authorized operation, the exact resulting catalog bytes and the provider's readback. An append-only event or a record hash alone must not be treated as proof that the signed request produced the persisted result.

## Root cause

The prior catalog validator checked action authorization, event append-only structure and per-record result hashes. The PR audit compared history length and prefix, but did not compare the signed expected_catalog_blob_sha with the exact base catalog bytes, did not bind the complete resulting catalog Git blob SHA to a provider-signed effect, and did not replay the operation. A candidate record or lifecycle status could therefore be changed while retaining an otherwise valid authorization event and updating the unsigned result_record_sha256.

## Selected design

- Preserve METHOD_KNOWLEDGE_CATALOG.json as the sole method authority.
- New method events carry effect_contract_version=1.0 and effect_receipt_ref.
- Store detached signed effects under knowledge/actions/<action_id>.effect.json.
- Sign exact action ID, domain, catalog path, operation, knowledge ID, previous/result catalog blob SHAs, canonical request SHA-256, exact authorization-attestation SHA-256, contract version and admission runtime.
- Require the same authenticated actor/provider for authorization and effect.
- Write catalog and effect receipt in one atomic bundle CAS and read back both exact blobs.
- Verify the complete persisted effect chain, action/nonce uniqueness, prior/result continuity and latest catalog SHA.
- In PR audit, verify the prior SHA against exact base bytes, require the effect receipt in the same changed-path set, verify its signature/result SHA and deterministically replay the signed operation against the prior catalog.
- Compare all replayed business fields; only recorded_at and updated_at are treated as non-business clock fields.
- Preserve historical events without effect receipts as explicitly unbound. Once effect-bound history begins, no later legacy event is accepted.

## Why not add another method ledger

A second catalog or action database would create duplicate authority and a consistency problem. The selected detached receipt is evidence only; the existing catalog remains canonical.

## Negative cases

- Missing, malformed, altered, replayed or wrong-path effect receipt.
- Wrong provider, actor, action, operation, request digest or authorization digest.
- Prior catalog SHA not equal to exact base bytes.
- Resulting catalog SHA not equal to exact candidate bytes.
- Discontinuous effect chain or repeated action/nonce.
- Catalog changes without an effect receipt in the same revision.
- Effect receipt changes without a catalog revision.
- Signed CHALLENGE request used to persist a different lifecycle result.
- Rollback to an unbound legacy event after effect-bound history.
- CI test signer presented as live provider evidence.

## Separate gates

A signed effect receipt does not activate a method. Independent promotion review, impact verification, affected-workflow replay, live authenticated provider deployment, native Skill activation, branch protection and external editorial/business outcomes remain separate gates. Synthetic CI can validate implementation behavior only.

## Evidence log

- Baseline main SHA: 0cabd473f4d9adaf687121a66f8f5701dfe606a2.
- Article-state effect repair PR #73: merged; merge SHA 0cabd473f4d9adaf687121a66f8f5701dfe606a2.
- Method-catalog candidate CI: PENDING.
- Live provider signer and atomic bundle CAS: OPEN.
- Independent promotion/impact reviewer: OPEN.
- Protected main / repository rulesets: OPEN.
