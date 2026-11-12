# Financial main-only branch archive — operator setup and stop conditions

**Scope:** D1traverser-debug/financial-writing-agent only. No CAOS repository, PR, setting, asset or runtime is touched.

## Live inventory at the 2026-11-12 audit

- Remote branches observed: **99**.
- Protected branches observed: **0**; main is currently unprotected.
- Open PRs observed: **#67** (fix(financial): independent semantic authority and release-acceptance guardrails).
- No branch or tag has been deleted by this repair.
- Candidate changes are on repair/financial-independent-acceptance-20261112; they are not yet the authoritative main.

## Why an owner-side setup is required

GitHub's delete-reference API does not provide compare-and-delete against an expected commit SHA. The archive script therefore refuses to prune unless the repository already has an active write-freeze ruleset and an immutable archive-tag ruleset, verifies a protected/reviewed main, reads a reviewer-protected GitHub Environment, and pins every observed branch head before attempting any deletion.

A successful local test or green CI cannot create these repository-level controls. The connected GitHub capability available to this repair can read and change repository files/PRs, but it cannot administer branch protection, rulesets, Environment reviewers or Actions secrets. Do not run the destructive workflow before completing the owner-side setup below.

## Required owner actions

### 1. Consolidate the code change first

Review and merge PR #67 only after its latest CI and independent source review are acceptable. Do not close it unmerged: doing so would preserve its commit as an archive tag but would leave the repair absent from main. After merge, verify the PR is closed/merged and that no other PR remains open.

### 2. Protect main

In GitHub repository Settings → Branches, add a branch protection rule for exactly main:

- Require pull requests before merging.
- Require the Financial CI status check before merge.
- Block force pushes and branch deletion.
- Ensure the rule makes the API report main.protected = true.

This rule is separate from the temporary write-freeze ruleset below.

### 3. Create the temporary branch write-freeze ruleset

Settings → Rules → Rulesets → New branch ruleset:

- Name: Financial archive write freeze.
- Enforcement: Active.
- Target: Branch.
- Include: ~ALL.
- Exclude: refs/heads/main.
- Rules: Restrict creations and Restrict updates.
- Bypass list: empty.

This freezes the candidate branch heads and prevents new branches from appearing during inventory/tag/readback/prune. It intentionally does not block deletion: every observed SHA is first pinned to an archive tag, and the script rechecks all live heads after pinning. Any moved/missing head blocks deletion of the remaining candidates.

### 4. Lock the archive-tag namespace

Create a tag ruleset:

- Name: Financial archive tag lock.
- Enforcement: Active.
- Target: Tag.
- Include: refs/tags/archive/financial-20261112/**.
- Rules: Restrict updates and Restrict deletions.
- Bypass list: empty.

This protects the immutable branch-head snapshots after the cleanup.

### 5. Configure the human approval Environment

Settings → Environments → create financial-branch-archive.

- Add at least one trusted required reviewer (preferably an independent reviewer).
- Enable prevention of self-review if the repository plan exposes that option.
- Do not store unrelated secrets in this Environment.

The workflow is manual-only and references this Environment. The reviewer approval is the actual human authorization; a Boolean input or a hard-coded workflow string is not treated as approval.

### 6. Add the narrowly scoped archive API credential

Create a fine-grained GitHub token restricted to this repository with:

- Administration: Read (to read Environment/ruleset configuration).
- Contents: Read and Write (inventory, create archive tags, delete branch refs).
- Pull requests: Read (to verify no open PR remains).
- Metadata: Read (GitHub's required repository metadata access).

Add it as an Environment secret named FINANCIAL_ARCHIVE_TOKEN under financial-branch-archive. Do not paste the token into chat, source files, commit history or ordinary workflow variables.

The workflow passes this secret only to the archive script. Its GITHUB_TOKEN variable name is an adapter interface; the credential comes from the Environment secret.

### 7. Execute only after all preconditions are visible

From the main branch, open Actions → “Financial one-time archive of obsolete branches” → Run workflow and set confirm_archive_prune = true. The required Environment reviewer must approve the deployment.

The script then independently checks:

1. Execution is on refs/heads/main and the live main SHA still equals the reviewed workflow SHA.
2. main is protected.
3. There are no open PRs and no other protected/active branch refs.
4. The required reviewer Environment and both active rulesets match their exact constraints.
5. Every observed non-main branch SHA is pinned under archive/financial-20261112/<original-branch-name>.
6. Every archive tag is read back at the exact SHA before any branch deletion starts.
7. Every live branch head is rechecked before deletion.
8. A complete post-run branch inventory equals exactly ["main"] and every archive tag is read back again.

Any failed precondition, ambiguous provider result, changed SHA, missing tag or incomplete final inventory stops the operation and leaves unresolved refs in place. There is no blind retry.

## Production runtime is a separate blocker

financial_writing_agent/provider_attestation.py now verifies HMAC-signed, audience-bound, time-limited provider attestations for owner messages, exact owner approvals and action authorization. This closes the previous code-level gap where a caller could return True or fabricate an authenticated_actor string.

It does not create a trusted signer or deploy a host API. Production still needs a provider that authenticates the real ChatGPT user, reads the original user message, issues signed attestations, performs GitHub CAS writes and independent readbacks, and protects signing keys outside model-visible input. The test signer and all pytest keys are synthetic and must never be deployed. The ChatGPT Skill is a guidance package, not this provider service.

Do not claim standalone production activation until that provider is deployed and tested from a fresh client session. This requires owner-side hosting/authorization setup; no credentials are requested in this document.

## Current stop status

**STOP — NO DESTRUCTIVE BRANCH PRUNE AUTHORIZED YET.**

At audit time main was unprotected, the archive Environment/rulesets were not verified, and PR #67 remained open. The repository must stay intact until the owner-side preconditions are configured and the candidate is merged.