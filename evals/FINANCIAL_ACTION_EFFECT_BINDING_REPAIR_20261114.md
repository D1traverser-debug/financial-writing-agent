# Financial action-effect binding repair — 2026-11-14

## Status

Candidate implementation in progress. The source baseline is main at 1c1ef8fe62fcf281face292836d371caef30cf87. No claim of merge, production acceptance, live provider activation or real article completion is made by this record. Exact candidate-head CI and post-merge readback are required before promoting the engineering result.

## Reconstructed goal

Financial Writing must not accept a business-state mutation merely because a provider signed an action request or a Git write returned a commit reference. The system must be able to prove that the authenticated action produced the exact state bytes now stored, that the receipt belongs to the same action and actor, and that the resulting effect was read back from the actual persistence provider. This must not introduce a second article state store or rewrite historical evidence.

## Root cause

The existing action authorization attestation bound action ID, task ID, operation, expected prior state SHA and request digest. The persisted execution receipt stored that authorization proof. However, it did not cryptographically bind the exact resulting STATE.json Git blob SHA to the authorization. The standalone runtime did read the state back, but the durable history retained no provider-signed receipt of that exact effect.

The PR-level repository audit also had a weaker path: it checked the signed authorization and selected owner transitions, but did not require a distinct effect receipt in the same Git revision or verify that its signed result SHA matched the candidate state bytes. Thus a valid authorization could be replayed as a claim about a different resulting state, and structural checks could not independently establish the exact persisted effect.

## Alternatives considered

1. Keep authorization-only receipts and trust the CAS writer's returned SHA. Rejected: the writer response is not durable provider-authenticated evidence and can be mismatched, forged or disconnected from the persisted bytes.
2. Put the resulting state SHA inside STATE.json. Rejected: this creates a self-reference because changing the embedded SHA changes the Git blob SHA being signed.
3. Store a separate signed effect receipt beside the canonical state and atomically commit both. Selected: the state contains only the receipt reference and contract version; the detached receipt signs the exact state blob SHA without self-reference. The existing article aggregate remains the only business-state owner.
4. Add a second journal/database for action effects. Rejected: duplicate authority and a new consistency problem.

## Selected contract

- STATE execution receipt authorization contract: 1.1.
- Detached provider effect receipt: 1.0 at workspaces/articles/<task_id>/actions/<action_id>.effect.json.
- The effect signature uses the same provider and authenticated actor as the authorization signature.
- Signed claims bind action ID, task ID, operation, previous state blob SHA or NEW_FILE, resulting state blob SHA, canonical request SHA-256, exact authorization-attestation SHA-256, effect contract version and admission runtime.
- STATE.json and its effect receipt are written in one atomic bundle CAS and both exact Git blobs are read back.
- The runtime verifies the complete historical effect chain, nonce/action replay protection, previous/result SHA continuity and the latest effect SHA against the current state SHA.
- A signed authorization v1.0 is preserved as legacy effect-unbound history. Existing receipts are not rewritten. A new v1.0 or unsigned receipt cannot follow an effect-bound v1.1 action.
- The PR audit requires the new effect receipt in the same changed-path set, create-only semantics, correct path, exact prior/result SHA and a provider signature verified against the exact candidate state bytes.

## Scope of implementation

- provider_attestation.py: verify the signed action_effect contract.
- standalone_runtime.py: create and verify detached effect receipts; require atomic bundle CAS; verify exact readback and complete history.
- whole_system_assurance.py: inspect effect receipt readbacks and reject state mutations without a signed, exact-result effect receipt.
- Tests: synthetic valid, missing, tampered, rollback, exact-state binding and native article workflow cases.
- Config/Skill/docs: make the new trust contract explicit without claiming the native ChatGPT Skill can sign provider receipts.

## Negative cases that must remain rejected

- Missing effect receipt or reader.
- Wrong provider, wrong authenticated actor, wrong action/task/operation or wrong request/authorization digest.
- Replayed action ID or provider nonce.
- Effect receipt path mismatch, rewrite or reuse.
- Resulting state SHA not equal to the exact candidate STATE.json Git blob SHA.
- Previous state SHA discontinuity.
- State-only CAS, non-atomic two-write sequence, mismatched provider response or failed second readback.
- Rollback from effect-bound v1.1 history to signed v1.0 or unsigned receipts.
- A CI fixture or model-authored record presented as live provider proof.

## Acceptance boundaries

Engineering acceptance requires exact-head CI, full tests, coverage, static/whole-tree checks and post-merge exact readback. Live system acceptance separately requires a genuinely authenticated provider that signs both authorization and effect, supports atomic conditional Git bundle writes and exact readback, plus the existing independent reviewer, native Skill/client activation and branch-protection gates. Real article quality and reader outcome remain separate. The active cross-border v3 article is not advanced or relabelled by this engineering repair.

## Evidence log

- Baseline main SHA: 1c1ef8fe62fcf281face292836d371caef30cf87.
- Prior main CI: 557 tests passed; 85% coverage threshold passed; whole-tree inventory parsed 308 tracked files; isolated wheel install passed; synthetic Word build/render passed.
- Candidate CI: PENDING.
- Independent reviewer: OPEN.
- Live provider signer and atomic bundle CAS: OPEN.
- Native Skill fresh-session activation: OPEN.
- Protected main / repository rulesets: OPEN.
- Real article and external reader outcome: OUT OF SCOPE / OPEN.
