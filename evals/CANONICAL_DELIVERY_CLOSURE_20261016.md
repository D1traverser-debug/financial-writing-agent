# Canonical Delivery Closure — 2026-10-16

Status: `CANDIDATE_IMPLEMENTED__VERIFICATION_PENDING`
Owner: `DOMAIN:financial_writing`
Parent upcall: `D1traverser-debug/universal-agent-os#63`
Domain problem record: `D1traverser-debug/financial-writing-agent#45`

## Governing outcome

A user-visible Financial Word delivery must reliably satisfy the already-owned output contract and presentation semantics without depending on the chat executor remembering formatting instructions. For current-kernel work with admitted private research, the user must also receive a private research Word copy.

## Observed failures

1. Live generated Deep/Broad Word files bypassed existing `document.py` / `checks.py` behavior: A-share names and key numeric anchors were not bolded as required and hierarchy was flattened.
2. `references/delivery.md` and current code already owned deterministic company bolding, semantic bold anchors and Chinese hierarchy, so the failure was not absence of those rules.
3. Product requirements permit a user-requested private research deliverable but the canonical `ArtifactKind` had no representation for that presentation artifact.
4. The user's no-`·` requirement was broader than the existing heading-prefix-only prohibition.

## Competing causal factors

- `MISSING_FORMAT_RULES`: rejected as primary; current Delivery authority and executable builder/checks already encode company bolding, semantic anchors and numbering.
- `SEMANTIC_AUDIT_TOO_WEAK`: rejected as intervention; an additional review can detect output drift but cannot prevent a host/executor from bypassing canonical construction.
- `CANONICAL_DELIVERY_PATH_BYPASS`: supported primary execution factor by live artifact behavior versus existing owner-native code.
- `PRESENTATION_CONTRACT_GAP`: supported contributor for private research and whole-document punctuation constraints.
- `HOST_COMPLETE_MEDIATION_GAP`: remains parent-level open boundary; Financial cannot prove native ChatGPT physically intercepts every possible pre-send path.

## Selected bounded intervention

Preserve the existing research/writing/owner-state architecture and close only the presentation boundary:

1. add `delivery_pipeline.py` as the canonical Word build/check/evidence path;
2. require explicit semantic bold anchors for Deep/Broad and at least one numeric bold anchor when material numeric facts are present;
3. normalize and fail-close forbidden visible characters, currently `·` -> `、`;
4. represent private research as `PRIVATE_RESEARCH_DOCX` without changing historical core `TaskContract.required_outputs` semantics;
5. require current-kernel states with an admitted `PrivateResearchBrief` to present that private Word as a supplemental visible output;
6. require every visible Word resource to carry digest-bound canonical build + mechanical + constraint + render + visual evidence before `VISIBLE_DELIVERY_READY`.

## Compatibility boundary

- Historical/core distribution-mode output semantics remain unchanged.
- `PRIVATE_RESEARCH_DOCX` is a supplemental presentation artifact, not a retroactive core owner-state required output.
- Historical states without a private-research marker are not retroactively forced to produce a private research Word.
- Owner article state remains the single business state authority; presentation evidence does not create a second state machine.

## Verification plan

Repository regression must prove:

- `·` is deterministically removed from final Word text;
- supplied A-share company names are bold at every occurrence;
- explicit key numeric anchor is bold;
- H1/H2 become `一、` / `（1）`;
- numeric long-form cannot build without an explicit numeric skim anchor;
- private research can be built as `PRIVATE_RESEARCH_DOCX` while core TaskContract outputs remain unchanged;
- visible delivery rejects missing/tampered canonical Delivery evidence;
- current private-research state rejects an incomplete visible resource set without `PRIVATE_RESEARCH_DOCX`;
- historical state without the marker remains compatible;
- full repository CI, wheel smoke and DOCX render smoke pass.

## Validation plan

After promotion, replay the live cross-border e-commerce delivery through the canonical path and visually inspect the regenerated files. Parent UAOS #63 remains open for the host-level complete-mediation boundary until parent evidence closes it.

## Evolution disposition

`DOMAIN_CHANGE_CANDIDATE__PARENT_HOST_BOUNDARY_REMAINS_OPEN`
