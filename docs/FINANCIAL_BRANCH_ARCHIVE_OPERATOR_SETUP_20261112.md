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

1. PLAN: read-only full inventory and SHA-256 manifest; no ref mutation. The schema-4 manifest records all 98 non-main branch heads, all merged-to-main PR head evidence, and a per-ref disposition. It explicitly separates 44 exact merged-PR heads from 54 refs without that exact evidence.
2. ARCHIVE: after a separate required-reviewer Environment approval, revalidate the exact manifest and create/read back an immutable archive tag for every non-main head while branch creation, update and deletion are all frozen. It deletes nothing.
3. PRUNE: after a second required-reviewer approval, and only after the owner removes the deletion rule while leaving creation/update frozen, verify the same manifest and every archive tag, then delete refs and perform a final full inventory. Because 54 refs lack exact merged-PR head evidence, the workflow exposes a separate `confirm_unverified_branch_archive` opt-in (default false). Without that explicit input, PRUNE is skipped; the archive tags remain and all branch refs are preserved.

The archive tags preserve the exact commits and their reachable Git history; they do not merge unique branch changes into main. Reviewers must inspect the 54 no-exact-PR entries and decide whether their contents are obsolete or need separate consolidation before approving the all-refs prune. This avoids silently treating "no exact PR match" as "safe to discard." The App token cannot create or update branches because those rules remain active. The deletion rule is removed only after every planned head is already preserved by an immutable tag.

## Required owner actions

### 1. Consolidate the code change first

Review and merge PR #67 only after its latest CI and independent source review are acceptable. Do not close it unmerged: that would preserve its commit in history but leave the repair absent from main. After merge, verify PR #67 is merged and no other PR remains open.

### 2. Protect main

In repository Settings → Branches, add a branch protection rule for exactly main:

- Require pull requests before merging.
- Require the Financial CI status check before merge.
- Block force pushes and branch deletion.
- Ensure the API reports main.protected = true.

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

- PLAN creates the schema-4 manifest artifact and prints its SHA-256. It does not mutate repository refs. Inspect the exact merged-PR classifications and the 54 no-exact-PR entries.
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


## Additional compare-to-main classification (2026-11-13)

A read-only GitHub compare was run for every unique SHA among the 54 refs without an exact merged-PR-head match. The 54 refs reduce to 34 unique commit heads:

- **25 refs / 8 unique heads** have `ahead_by = 0` and `behind_by > 0`: their tip commits are already ancestors of main. They are stale/duplicate refs; their archive tags still must be verified before deletion.
- **27 refs / 24 unique heads** are divergent with commits ahead of main. These contain unique historical commits and must be preserved and reviewed before any prune.
- **1 ref** is the current open PR #67 candidate. It is ahead of main and must remain until review and merge.
- **1 ref**, `research/cross-border-v3-source-revalidation-20261018`, has one unique commit ahead of main. It contains a task-specific source-revalidation report and must be reviewed separately; it does not itself admit or publish the article.

Two concrete historical samples were inspected:

- `article/ai-security-infrastructure-2026-10-12-7f3a91c2` contains a complete article draft and task state at FINAL_AUDIT, but its review assurance is `CHAT_SELF_REVIEW` and certification remains OPEN. Do not treat it as an independently accepted article or delete its history without owner review.
- The older `writing-system-gap-hardening` head contains a Cloudflare Site/D1/R2 MCP proof-of-concept. Its `SiteDispatcher.call` delegates to `FailClosedDispatcher`; `MIGRATION_STATUS.md` explicitly says business execution for all 16 tools is not wired and real-article live-model E2E remains 0. It is historical design evidence, **not a usable hosted Financial runtime**.

This compare classification improves the earlier "no exact PR match" signal but does not replace the reviewed archive manifest. No merge, article-state mutation, branch deletion or tag creation was performed during this read-only review.
