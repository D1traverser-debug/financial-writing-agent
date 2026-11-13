# Financial main-only branch archive — operator setup and stop conditions

Scope: D1traverser-debug/financial-writing-agent only. No CAOS repository, PR, setting, asset or runtime is touched.

## Live inventory at the 2026-11-12 audit

- Remote branches observed: 99 (main + 98 non-main refs).
- Protected branches observed: 0; main is currently unprotected.
- Pull request inventory: 67 total records (48 merged into main, 18 closed without merge, and the sole open PR #67).
- Exact merged-PR head matching: 44 branch refs point to a head SHA that appears as the head of a merged PR into main; 54 branch refs have no exact merged-to-main PR head evidence. "No exact PR match" is not proof of unmerged content: squash merges, direct commits, stale refs and duplicate heads may explain it.
- GitHub rulesets API currently returns an empty list: neither the branch freeze nor archive-tag lock is configured.
- The connected GitHub read surface cannot verify the two required-reviewer Environment settings; the archive workflow will fail closed unless both are configured.
- CI's read-only dry-run confirmed 99 branches and 1 open PR, with no ref mutation.
- No branch or tag has been deleted by this repair.
- Candidate code is on repair/financial-independent-acceptance-20261112, not yet authoritative main.

## Why cleanup is a two-phase operation

GitHub's delete-reference API has no compare-and-delete against an expected SHA. A client-side GET followed by DELETE is not sufficient if branch refs can move or disappear concurrently.

The implemented workflow therefore has three jobs:

1. PLAN: read-only full inventory and SHA-256 manifest; no ref mutation. The schema-5 manifest records all 98 non-main branch heads, all merged-to-main PR head evidence, and a per-ref disposition. It explicitly separates 44 exact merged-PR heads from 54 refs without that exact evidence.
2. ARCHIVE: after a separate required-reviewer Environment approval, revalidate the exact manifest and create/read back an immutable archive tag for every non-main head while branch creation, update and deletion are all frozen. It deletes nothing.
3. PRUNE: after a second required-reviewer approval, and only after the owner removes the deletion rule while leaving creation/update frozen, verify the same manifest and every archive tag, then delete refs and perform a final full inventory. Because 54 refs lack exact merged-PR head evidence, the workflow exposes a separate `confirm_unverified_branch_archive` opt-in (default false). Without that explicit input, PRUNE is skipped; the archive tags remain and all branch refs are preserved.

The archive tags preserve the exact commits and their reachable Git history; they do not merge unique branch changes into main. Reviewers must inspect the 54 no-exact-PR entries and decide whether their contents are obsolete or need separate consolidation before approving the all-refs prune. This avoids silently treating "no exact PR match" as "safe to discard." The App token cannot create or update branches because those rules remain active. The deletion rule is removed only after every planned head is already preserved by an immutable tag.

## Required owner actions

### 1. Consolidate the code change first

Review and merge PR #67 only after its latest CI and independent source review are acceptable. Do not close it unmerged: that would preserve its commit in history but leave the repair absent from main. After merge, verify PR #67 is merged and no other PR remains open.

### 2. Protect main

In repository Settings → Branches, add a branch protection rule for exactly main:

- Require pull requests before merging.
- Require at least one approving review.
- Dismiss stale approvals when new commits are pushed.
- Require approval of the latest reviewable push.
- Enforce the protection rule for administrators (no admin bypass).
- Require the exact Financial CI status check context `test`.
- Block force pushes and branch deletion.
- Ensure the API reports `main.protected = true`.

This is separate from the temporary archive ruleset.

### 3. Create the temporary branch freeze ruleset

Settings → Rules → Rulesets → New branch ruleset:

- Name: Financial archive write freeze.
- Enforcement: Active.
- Target: Branch.
- Include: ~ALL.
- Exclude: refs/heads/main.
- Rules: Restrict creations, Restrict updates, and Restrict deletions.
- Bypass list: empty.

This must be active before PLAN starts. It stabilizes the branch inventory and prevents any actor from moving, creating or deleting a non-main ref while the plan and tag phase run.

### 4. Lock the archive-tag namespace

Create a tag ruleset:

- Name: Financial archive tag lock.
- Enforcement: Active.
- Target: Tag.
- Include: refs/tags/archive/financial-20261112/**.
- Rules: Restrict updates and Restrict deletions.
- Bypass list: empty.

The script requires the bypass_actors field to be visible and empty. If GitHub omits it for the caller, the workflow fails closed rather than assuming no bypass exists.

### 5. Configure two required-reviewer Environments

Create both environments:

- financial-branch-archive
- financial-branch-prune

For each:

- Add at least one trusted required reviewer, preferably an independent reviewer.
- Enable prevention of self-review if available.
- Keep the archive App private key scoped to these environments.

The first reviewer sees the plan artifact and approves creation of tags only. The second reviewer approves the prune job only after all tags have been verified and the owner has removed the branch deletion rule. The script checks that reviewer protection is configured; GitHub Actions Environment approval is what gates the actual job. The script does not pretend a GET of environment settings proves approval of a particular run.

### 6. Create a narrowly scoped GitHub App for the write phases

Create a GitHub App and install it only on D1traverser-debug/financial-writing-agent.

Grant repository permissions required by the workflow:

- Administration: Write (needed to read ruleset bypass_actors with full visibility).
- Contents: Write (create archive tags and delete branch refs).
- Pull requests: Read.
- Environments: Read.
- Metadata: Read.

Set repository variable FINANCIAL_ARCHIVE_APP_ID to the App ID. Add the App private key as FINANCIAL_ARCHIVE_APP_PRIVATE_KEY in both required-reviewer Environments. The workflow mints a short-lived installation token scoped to this one repository and revokes it at job completion.

The App has powerful repository permissions, so keep the private key in Environment secrets and do not expose it to the PLAN job or chat.

### 7. Create a temporary read/manifest credential

The PLAN job must inspect repository rulesets and their bypass actors before taking the inventory. Create a short-lived fine-grained token restricted to this repository with:

- Administration: Write (required for full ruleset bypass-actor visibility).
- Contents: Read.
- Pull requests: Read.
- Environments: Read.
- Metadata: Read.

Store it as repository Actions secret FINANCIAL_ARCHIVE_READ_TOKEN. It is used only by the read-only PLAN job; the script performs GET requests only in that phase. Revoke the token after the plan/archive/prune operation. If the token cannot expose bypass_actors, the script stops.

### 8. Run the staged workflow

From main, open Actions → Financial one-time archive of obsolete branches → Run workflow and set start_archive = true.

- PLAN creates the schema-5 manifest artifact and prints its SHA-256. It does not mutate repository refs. Inspect the exact merged-PR classifications and the 54 no-exact-PR entries.
- ARCHIVE waits for the financial-branch-archive reviewer approval. The reviewer should inspect all 98 non-main names/SHAs and approve only if every head is intended to be preserved as an immutable tag. The job creates and verifies all archive tags; it does not delete branches.
- After ARCHIVE succeeds, edit the Financial archive write freeze ruleset and remove only Restrict deletions. Keep Restrict creations and Restrict updates active. Do not change the tag lock or bypass list.
- If any no-exact-PR branch contains work that must enter main, stop and consolidate that work before pruning. Otherwise explicitly set `confirm_unverified_branch_archive=true` when dispatching the workflow to opt into pruning all archived non-main refs.
- PRUNE then waits for the financial-branch-prune reviewer approval. The reviewer should verify the archive-phase readback, the explicit opt-in, and that the deletion rule was removed while creation/update remain frozen. Approve only then.

The script checks that the reviewed manifest digest still matches the live branch inventory, main SHA and protection remain unchanged, no open PR exists, every tag matches the original head, and the final branch inventory is exactly [main]. During PRUNE it re-reads main protection plus the branch creation/update freeze and archive-tag lock before each deletion, then verifies those controls again after the final inventory. If any control is removed or changes, pruning stops and all archive tags remain.

Operational constraint: do not create, close or retarget pull requests during the cleanup window. The script rechecks open PRs before each deletion and after completion, but GitHub has no repository ruleset that atomically freezes PR creation. An open-and-closed PR between checks cannot be ruled out by the branch-ref API. If PR activity cannot be paused, do not run PRUNE.

Any failed precondition, ambiguous provider result, changed SHA, missing tag or incomplete final inventory stops the operation. A partially completed prune still leaves all archived tags in place; rerun only after investigating the recorded report.

### 9. After successful cleanup

- Verify the final report shows complete = true, after_branch_names = [main], and all planned archive tags read back at their exact SHAs.
- Revoke FINANCIAL_ARCHIVE_READ_TOKEN.
- The App installation token is automatically revoked at the end of each job.
- Keep the archive-tag lock and main protection.
- Remove the temporary branch write-freeze ruleset if future feature branches are required. The final cleanup state is one main; leaving the freeze active would prohibit future branch creation/update.

## Production runtime is a separate blocker

financial_writing_agent/provider_attestation.py verifies HMAC-signed, audience-bound, time-limited provider attestations for owner messages, exact owner approvals and action authorization. It closes the code-level gap where a caller could return True or fabricate an authenticated_actor string.

It does not create a trusted signer or deploy a host API. Production still needs a provider that authenticates the real ChatGPT user, reads the original user message, issues signed attestations, performs GitHub CAS writes and independent readbacks, and protects signing keys outside model-visible input. The test signer and pytest keys are synthetic and must never be deployed. The ChatGPT Skill is a guidance package, not this provider service.

## Current stop status

STOP — NO DESTRUCTIVE BRANCH PRUNE AUTHORIZED YET.

At audit time main was unprotected, the archive Environments/rulesets were not verified, and PR #67 remained open. Keep all existing refs until owner-side controls are configured, PR #67 is merged, and the staged workflow has passed its read-only plan and tag-verification phase.

## Required G7 readback evidence

The final signed Financial main-hygiene gate must include all of the following, not merely a one-branch count:

- SHA-256 of the exact reviewed archive manifest.
- A successful tag-by-tag readback proving each archived branch head is preserved.
- SHA-256 of the final remote branch inventory.
- `main.protected = true`, pull requests required, at least one approving review required, force pushes disabled, and branch deletion disabled.
- The Financial CI job context `test` required by the main protection rule.
- Final branch names exactly `["main"]`, with one verified archive tag per original non-main branch.

The system acceptance evaluator rejects missing or contradictory fields. These are evidence requirements, not claims that repository administration has already been configured.



## Full no-exact-merged-PR branch-head classification (read-only, 2026-11-13)

The 54 unverified refs reduce to 34 unique commit heads. The table records the current branch-name grouping and the disposition selected from read-only comparisons and representative source inspection. The schema-5 live manifest remains the final SHA-bound inventory at execution time.

| Unique head | Branch ref(s) | Compare-to-main class | Review disposition |
|---|---|---|---|
| `ec87c775c474f7226ac9771961d7b743e4e165d8` | `article/ai-security-infrastructure-2026-10-12-7f3a91c2` | Diverged | Article/task snapshot; FINAL_AUDIT is CHAT_SELF_REVIEW and certification OPEN. Preserve task history; not system code or accepted publication. |
| `36919f6d9cb99ffd373d6a6d6be446743ff99791` | `article/fw-20261012-ai-security-6dd14859-canonical`, `article/fw-20261012-ai-security-6dd14859-exec`, `article/fw-20261012-ai-security-6dd14859-final`, `article/fw-20261012-ai-security-6dd14859-live`, `article/fw-20261012-ai-security-6dd14859-run`, `article/fw-20261012-ai-security-6dd14859-state`, `article/fw-20261012-ai-security-6dd14859-state2`, `article/fw-20261012-ai-security-6dd14859-work`, `article/fw-20261012-ai-security-6dd14859`, `maintenance/fresh-chat-authority-20261012` | Ancestor | One shared SHA already reachable from main; duplicate article/run aliases. Archive after tag readback. |
| `45658bd95128c38b07de8d561124ff6a7914bc33` | `article/2026-10-15-huangjiu-high-end-channel` | Ancestor | Historical article branch already reachable from main; archive after tag readback. |
| `bebd3ef04e18ac738fee00701cccaa9c5a7eba7a` | `editorial-density-compliance-hardening` | Diverged | Legacy runtime/Site PoC line; preserve as alternative history, do not merge wholesale. |
| `2530215e1ba5ea5377a1bf7f8c5fa4f93901e7f5` | `final-evidence-hardening` | Diverged | Legacy runtime/Site PoC line; preserve as alternative history. |
| `e580cd4dfda8db47674803451c9adfff9e3cf975` | `fix/financial-current-lineage-tamper-20261018; fix/parent-governed-financial-lineage-invariant-20261018` | Ancestor | Two refs share one SHA already reachable from main; archive after tag readback. |
| `23530f2e34ef4b137c749c261e05e978e4af9d12` | `hotfix/financial-writing-1.0.2-authoritative-state-20261015` | Diverged | Old authoritative-state/candidate-integrity modules. Current admission, owner guard/lifecycle and standalone runtime are the selected replacement; preserve old code/tests, do not merge by filename. |
| `af5fe1ca3b6d6ffecd6179b57528b529875d015c` | `human-voice-headline-craft-20261009` | Diverged | Older editorial/style experiments on legacy runtime line; preserve; any style reuse must be checked against current Financial references. |
| `9fca4081fd296aee634f9e4858f7696ddaca5642` | `maintenance/continuity-v2-runtime-parity-20261009` | Diverged | Site PoC plus continuity-v2 runtime port; not selected production runtime. |
| `95b6cb98e2470516d4270fbe7ad87550d0bd13cb` | `maintenance/continuity-v2-task-metadata-writing-20261009` | Diverged | Site PoC plus task-metadata port; preserve as alternative implementation history. |
| `efe1341435b4b5f485dc655914c44e20b823a37d` | `maintenance/domain-identity-decoupling-20261014` | Diverged | UAOS-bound identity/adapter work; current candidate removes parent-runtime dependency. |
| `182b9049d6c95f003942419e8a8f8b3c7aec6ce1` | `maintenance/github-chat-branch-discovery-20261012` | Diverged | Older GitHub-chat branch discovery/continuity path; current candidate uses owner-native standalone authority. |
| `2efb69cc6f0a96703c0a888188ad656534ea50d3` | `maintenance/github-chat-runtime-20261012` | Diverged | Older GitHub-chat runtime/store path; preserve as superseded implementation history. |
| `3b4604f96b55b8bf1579f266ebd9bbbc744a0b00` | `maintenance/owner-local-integrity-20261013` | Diverged | Earlier GitHub-chat lifecycle/owner-integrity design; current candidate uses owner-native state and provider attestations. |
| `9042c33671c3dc926a68968260464bd3ad4befac` | `maintenance/persistent-asset-profile-20261017` | Diverged | Asset profile explicitly inherits UAOS parent policy; not a standalone Financial authority. Preserve as historical inventory evidence. |
| `1948a9f80275aad202955c932430d7c882c82c97` | `maintenance/phase1-workflow-kernel-20261012` | Ancestor | Phase-1 kernel tip already reachable from main; archive after tag readback. |
| `208280dc61ea7e23c2612ddb494a5bc6cecf58a4` | `maintenance/phase2-state-recovery-20261012` | Ancestor | Phase-2 recovery tip already reachable from main; archive after tag readback. |
| `180f0986f37503d7adde2d8da95e1b0c5ffe89bf` | `maintenance/phase3-specialist-boundaries-20261012` | Diverged | Earlier multi-specialist contracts are an alternative design; selected runtime does not require that orchestration layer. |
| `b8deba8fea5d02e1e1108f16c5486c8e0b3d348a` | `maintenance/uaos-article-binding-20261014` | Diverged | UAOS article-binding adapter conflicts with current no-parent-runtime boundary; preserve only. |
| `7763d4ea287c4b45a4dfd3ad045547f7169694b5` | `maintenance-autonomy-hardening` | Diverged | Legacy Site/runtime branch; preserve as alternative implementation history. |
| `16a00ea92e43a6c211ab2c3ab2af3194cdd8c9ea` | `narrative-finance-style-hardening-20261008` | Diverged | Earlier editorial/style work on legacy runtime line; preserve; compare with current style reference before reuse. |
| `086315bbf42cde424a36daeb4c6a53557c6450be` | `predeploy-hardening-actual`, `predeploy-hardening-base`, `predeploy-hardening-ci`, `predeploy-hardening-final`, `predeploy-hardening-work` | Ancestor | Five refs share one historical SHA already reachable from main; archive after tag readback. |
| `ce6353fe69aadf50f37275c90864442e2564890d` | `predeploy-hardening-noop`, `predeploy-hardening-types-base`, `typed-tools-scratch` | Diverged | Older skill/engine/MCP implementation. Current candidate uses a different owner-native runtime and delivery pipeline; preserve as historical design. |
| `0484e9620d49d8256672130e26cac0073f9bf376` | `professional-analysis-hardening` | Diverged | Legacy Site/runtime line; preserve as alternative implementation history. |
| `7ae3b8e9e755e55874f8750e5146e6d36f571cc9` | `reader-value-learning-hardening` | Diverged | Legacy Site/runtime and reader-value experiment; preserve. Current reader-value references remain selected authority. |
| `PR #67 head` | `repair/financial-independent-acceptance-20261112` | Candidate | Keep open for independent review and exact-head CI; do not prune or merge before required review and system gates. |
| `eb420499e07e76214ac861d83ae99badb8e006d4` | `research/cross-border-v3-source-revalidation-20261018` | Ahead of main | One unique commit containing task-specific source-revalidation evidence; preserve separately, does not admit or publish the article. |
| `cda850e1e746f8ee8b1077189827e252b4bc097c` | `test/github-chat-guard-tracer-20261012` | Diverged | Earlier GitHub-chat guard/tracer; current provider-attestation and standalone-runtime boundaries supersede its execution model. |
| `07874059e8017f80154df3546fc25887a9cc9914` | `tmp-noop-should-not-use; tmp-noop-should-not-use-2` | Ancestor | Two no-op refs share one historical SHA already reachable from main; archive after tag readback. |
| `56f41a70338319db2465854ec7bbc74f43fb93fa` | `tmp-should-not-create`, `tmp-should-not-create-2`, `tmp-should-not-create-3`, `tmp-should-not-create-4` | Ancestor | Four no-op refs share one historical SHA already reachable from main; archive after tag readback. |
| `22e30e399e33472771c60a61d86829a8d40ba439` | `uaos/common-behavior-1-3-root-scope` | Diverged | UAOS/common-behavior and problem-action-admission experiment; current Financial cognition/intent governance is selected. |
| `1703aeadeeeb13362657e3eb6c031cf454542808` | `v0.2.1-runtime-rule-hardening` | Diverged | Site PoC/runtime rule-hardening line; preserve as alternative, non-production deployment history. |
| `dee14a448650201bbfed408385060d34e65ed4db` | `v0.2.1-writing-agent-integrated` | Diverged | Site PoC integrated branch; business tool dispatch remains fail-closed; preserve, do not promote. |
| `2494a21e0248e9482065189c875ffd74c3ba820c` | `writing-system-gap-hardening` | Diverged | Most developed historical Site/D1/R2 PoC; SiteDispatcher.call uses FailClosedDispatcher and 16-tool business execution is not wired. Archive-only, not production. |

**Disposition totals:** 26 refs / 8 unique heads are already ancestors of main; 26 refs / 24 unique heads are divergent and contain unique historical commits; one additional ref is the current PR #67 candidate; one is the cross-border source-revalidation note. The article branch and source-revalidation branch are task evidence, not system code. The legacy runtime/Site/UAOS branches are preserved as alternative historical implementations, not merged into the selected standalone architecture. The archive tags must preserve every branch head before any ref is deleted. This table does not replace the final live manifest or authorize destructive pruning.

## Additional compare-to-main classification (2026-11-13)

A read-only GitHub compare was run for every unique SHA among the 54 refs without an exact merged-PR-head match. The 54 refs reduce to 34 unique commit heads:

- **26 refs / 8 unique heads** have `ahead_by = 0` and `behind_by > 0`: their tip commits are already ancestors of main. They are stale/duplicate refs; their archive tags still must be verified before deletion.
- **26 refs / 24 unique heads** are divergent with commits ahead of main. These contain unique historical commits and must be preserved and reviewed before any prune.
- **1 ref** is the current open PR #67 candidate. It is ahead of main and must remain until review and merge.
- **1 ref**, `research/cross-border-v3-source-revalidation-20261018`, has one unique commit ahead of main. It contains a task-specific source-revalidation report and must be reviewed separately; it does not itself admit or publish the article.

Two concrete historical samples were inspected:

- `article/ai-security-infrastructure-2026-10-12-7f3a91c2` contains a complete article draft and task state at FINAL_AUDIT, but its review assurance is `CHAT_SELF_REVIEW` and certification remains OPEN. Do not treat it as an independently accepted article or delete its history without owner review.
- The older `writing-system-gap-hardening` head contains a Cloudflare Site/D1/R2 MCP proof-of-concept. Its `SiteDispatcher.call` delegates to `FailClosedDispatcher`; `MIGRATION_STATUS.md` explicitly says business execution for all 16 tools is not wired and real-article live-model E2E remains 0. It is historical design evidence, **not a usable hosted Financial runtime**.

This compare classification improves the earlier "no exact PR match" signal but does not replace the reviewed archive manifest. No merge, article-state mutation, branch deletion or tag creation was performed during this read-only review.


## Native Skill release alignment — G5 remains open

The private ChatGPT plugin currently reports release `0.1.1` (`pluginrel_6af5a82a95f48191ba8d21fa3d188094`). Its installed package is skill-only, has no hosted Python/MCP endpoint, and its current Skill text still treats one authenticated user utterance as one atomic requirement. The candidate repository Skill has corrected this: it preserves the complete authenticated utterance as source evidence while allowing multiple scoped requirement records, provided the exact canonical mutation receives a separate signed owner confirmation.

Do not publish a plugin release ahead of main. After PR #67 is independently reviewed and merged, update the private plugin from the exact main Skill and its current Financial references, read back the new release ID/content, update `config/FINANCIAL_MANIFEST.json` and `config/CHATGPT_FINANCIAL_PLUGIN.json` to that exact release, then verify a fresh ChatGPT session and a real Financial tool invocation. The current `0.1.1` package must not be represented as equivalent to the candidate Skill, and a private package release alone does not prove user installation or a live provider.


### Main protection is now verified as a live control, not a boolean

The archive script's schema-5 plan reads `GET /branches/main/protection` and rejects the plan unless the actual protection response proves all of the following:

- `required_pull_request_reviews` exists and `required_approving_review_count >= 1`, `dismiss_stale_reviews = true`, and `require_last_push_approval = true`;
- `enforce_admins.enabled = true`, so repository administrators cannot bypass the main protection rule;
- `required_status_checks` includes the exact Financial CI context `test` (from either contexts or checks);
- `allow_force_pushes.enabled = false`;
- `allow_deletions.enabled = false`.

The normalized protection snapshot is embedded in the manifest and its SHA-256. PLAN and ARCHIVE re-read it; PRUNE re-reads it before each deletion and after the final inventory, requiring exact equality with the reviewed snapshot. A protection change that remains superficially "valid" (for example, changing the approval count) also stops the prune. Missing protection fields fail closed. Unit tests cover missing CI, missing PR requirement, zero approvals, force-push/deletion enabled, and protection changes before or during prune.
