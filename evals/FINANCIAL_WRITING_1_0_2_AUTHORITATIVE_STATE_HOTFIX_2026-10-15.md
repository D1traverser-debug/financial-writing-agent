# Financial Writing 1.0.2 authoritative-state hotfix

Status: CANDIDATE
Date: 2026-10-15

## Trigger

Final review of the 1.0.1 candidate found three P1 bypasses after the PR had already been merged:

1. current quality dispatch could be downgraded by deleting or changing caller-controlled `writing_kernel_version` state fields;
2. a process-local sequencing token was reachable by callers and accepted by public guard APIs;
3. quality evidence plus its digest could be rewritten together inside the same caller-controlled state object.

The incident also exposed a review-governance failure: `Completed` review status was treated as equivalent to `no findings`. This hotfix therefore requires explicit review-thread/finding inspection before promotion.

## Selected mechanism

The candidate moves mutation admission from state self-attestation to owner-native GitHub state authority:

- resolve `workspaces/articles/{task_id}/STATE.json` from `main` before every material mutation;
- require the caller state to equal the authoritative persisted state;
- require `previous_state_blob_sha` to equal GitHub's current blob SHA;
- introduce schema `1.3` for quality-governed current states, while retaining 1.1/1.2 historical compatibility;
- make every public new-task builder create schema 1.3 + writing kernel 1.0; historical schemas are compatibility inputs, not selectable new-task modes;
- keep writing kernel `1.0` and capability profile `18` because no new UAOS common capability is introduced;
- remove public sequencing-token parameters;
- atomically parse quality evidence, create the transition receipt, bind quality digests, and validate the resulting unpersisted state inside the canonical Owner guard;
- apply the same authoritative mutation precondition to feedback, blocked recovery, system-impact lifecycle, and proactive-resolution mutations.

## Rejected alternatives

1. **Add more caller-supplied hashes/signatures inside STATE** — rejected because the same caller can rewrite evidence and its self-contained digest chain together.
2. **Keep a private-looking bypass token** — rejected because Python module attributes are reachable and the public API had accepted the token directly.
3. **Trust `writing_kernel_version` alone to distinguish current from legacy** — rejected because the marker itself is caller-controlled until compared with persisted authority.
4. **Keep a public legacy-task constructor for tests/compatibility** — rejected because that creates a birth-time opt-out from current governance. Tests that need historical semantics now construct an explicit historical fixture instead.
5. **Turn all unit tests into live GitHub integration tests** — rejected because this would make deterministic semantic tests dependent on network state. Ordinary pytest tests stub only the private authoritative-resolution boundary; dedicated `strict_authority` regressions exercise the production boundary with explicit immutable snapshots.

## Required regressions

- changing/removing current marker/schema cannot downgrade a persisted 1.3 task;
- recomputing a quality digest in the same tampered candidate state does not establish authority;
- public guard mutation signatures expose no quality-validation bypass token;
- public new-task construction cannot create a fresh 1.1/1.2 task;
- proactive-resolution and lifecycle mutation paths reject candidate state that differs from persisted authority;
- old 1.1/1.2 states remain readable/recoverable under historical compatibility;
- package/wheel smoke identifies 1.0.2 + schema 1.3 current tasks;
- full unit, contract, static, retired-runtime, wheel and DOCX-render CI remains green;
- final-head review must be inspected for actual unresolved findings, not merely completion status.

## Assurance boundary

The authoritative GitHub `main` state + blob SHA is external to the in-process candidate mapping, so it closes the reviewed self-attestation bypasses inside Financial owner mutations. It is **not** a cryptographically immutable ledger and does not claim to prevent a repository administrator or another out-of-band writer from directly rewriting `main` outside the Financial guard. Prevention/admission of such host-level writes remains governed by UAOS mutation-sentinel and authority-write policy. Financial 1.0.2 must therefore report executable/trajectory assurance, not administrator-proof immutability or independent certification.

## Remaining question before promotion

No known architecture question remains from the three 1.0.1 P1 findings. Promotion remains blocked on final-head CI, adversarial review, explicit inspection of unresolved review threads, and production reread after merge.
