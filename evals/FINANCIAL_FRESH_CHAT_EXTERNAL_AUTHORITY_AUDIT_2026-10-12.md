# Financial Writing Fresh-Chat / External Authority Audit — 2026-10-12

Status: `OWNER_AND_EXTERNAL_POINTER_DRIFT_REPAIRED__PRODUCT_FRESH_CHAT_TRACE_OPEN`

## Purpose

Verify that Financial Writing does not depend on stale chat memory, stale Library/Notion pointers, or obsolete execution modes, and distinguish owner readiness from product-level automatic fresh-chat discovery.

## Confirmed defects found

1. `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` still referenced execution capability profile 9 while `continuity/EXECUTION_CAPABILITIES.json` is profile 10.
2. `continuity/tasks/financial-writing-main/HANDOFF.md` still described the older owner-native/Standalone-era state instead of current GITHUB_CHAT + Phase-1 workflow kernel + Phase-2 state/recovery semantics.
3. ChatGPT Library `/A股超短系统/00_写作Agent_新对话恢复入口.md` pointed to retired `v0.2.1-writing-agent-integrated` and `STANDALONE_SKILL/ShadowTaskLedger` fallback.
4. ChatGPT Library had a redundant older root-level `00_A股系统_新对话接班指引.md` alongside the scoped current copy.
5. Notion `A股超短系统｜知识导航（非全局恢复入口）` copied the old Financial branch/Standalone routing text and an old Continuity version description.
6. ChatGPT Library root Continuity pointer still said v3.6 and copied an obsolete broad startup read list instead of the current v3.7 thin bootstrap invariant.

## Repairs completed

### Financial owner repository

- `TASK_MANIFEST.json` reconciled in place to manifest version 19 / execution capability profile 10 while preserving `resume_epoch=2` and the existing active lease.
- `HANDOFF.md` replaced with current owner truth:
  - one canonical business workflow from `financial_writing_agent/workflow_spec.py`;
  - OWNER_NATIVE versioned WritingState + checkpoint CAS/recovery;
  - guarded GITHUB_CHAT as the bounded non-owner-native adapter;
  - no free-form/Standalone fallback;
  - NEW_TASK vs explicit continuation semantics;
  - current assurance boundaries.
- `continuity/TASK_INDEX.md` aligned with profile 10 and explicitly records that generic fresh-chat product discovery is a separate product/account capability that the repo cannot self-certify.

### ChatGPT Library

- `/A股超短系统/00_写作Agent_新对话恢复入口.md` replaced by v4 thin pointer:
  - GitHub `financial-writing-agent@main` only;
  - profile 10 handshake;
  - OWNER_NATIVE or guarded GITHUB_CHAT;
  - retired `STANDALONE_SKILL/ShadowTaskLedger` cannot be restored;
  - external stores are reference/bootstrap/evidence only;
  - fresh-chat discovery boundary stated explicitly.
- `/A股超短系统/00_A股系统_新对话接班指引.md` Financial section updated to `main` + profile 10 + guarded GITHUB_CHAT.
- redundant root-level old `00_A股系统_新对话接班指引.md` moved to trash.
- root `/00_跨对话继承_唯一入口.md` updated to Universal Continuity v3.7 and reduced to the current two-file bootstrap (`ENTRYPOINT.md` + `CURRENT_PROTOCOL.json`) plus event-driven loading.

### Notion

`A股超短系统｜知识导航（非全局恢复入口）` was updated so active Financial routing now points to:

- GitHub `financial-writing-agent@main`;
- capability profile 10;
- owner-native when actually available;
- otherwise guarded GITHUB_CHAT only when model + GitHub owner R/W + deterministic guard + stage tools are observed;
- Standalone/ShadowTaskLedger retired;
- Universal Continuity engineering authority is GitHub main / v3.7, while Library is only a thin bootstrap pointer.

Historical Notion pages such as `[已废弃] CURRENT_CHAT_HANDOFF｜旧写作聊天缓存` remain as explicit tombstones/evidence and are not active authority. `PENDING_REVIEWQUEUE｜写作发现待正式复盘` remains knowledge/review evidence only and explicitly cannot restore a Financial task.

### Google Drive

No active Financial routing repair was needed:

- `00_ROUTER_系统入口与任务路由` already declares `financial-writing-agent@main` as the sole Financial rule/execution authority and constrains Drive/Notion to reference/knowledge roles.
- exact searches for `v0.2.1-writing-agent-integrated`, `STANDALONE_SKILL`, and `ShadowTaskLedger` returned no Drive matches.
- `profile 9` only appeared in historical/audit material, not the active Financial router.

## Duplicate / legacy policy

Do **not** delete historical evidence merely because it contains old terms. Cleanup rule:

- active-looking duplicate/shadow authority → remove, replace, or tombstone;
- generated package mirrors that are byte-for-byte checked by the owner harness → keep as controlled mirrors, not duplicate authority;
- historical audits/final articles/tombstones → retain as evidence but never route execution from them.

The root-level duplicate A-share handoff was removed because it was active-looking shadow routing. Historical writing audits and decommissioned Notion pages remain intentionally.

## Current fresh-chat conclusion

### Owner execution readiness

Once a conversation is actually routed to the Financial owner and has the required current-session capabilities, the current GitHub owner can execute via the formal workflow rather than free-form prose:

`Financial intent → current main Skill/manifest/profile 10 → capability handshake → OWNER_NATIVE or guarded GITHUB_CHAT → durable article state → canonical workflow`

### Product/account discovery — still OPEN

This audit does **not** prove that every completely new ChatGPT conversation will automatically read GitHub/Library and select Financial merely because the user says “写一篇财经文章”.

Current Universal authority explicitly states:

- GitHub/Library are not automatic event listeners;
- explicit continuation depends on an account/product startup hook;
- a real new-owner/fresh-chat product trace is required for open-world automatic-discovery claims.

Therefore the remaining gate is:

`REAL_FRESH_CHAT_NORMAL_FINANCIAL_INTENT_ROUTE_TRACE`

A passing trace must start from a genuinely new product chat, with no “继承/继续/恢复” and no hint such as “用 GitHub 财经系统”, give only a normal financial-writing request, and observe whether the product/account routing layer autonomously selects current Financial authority before research/drafting. If it does not, that is a product/account routing defect, not a Financial workflow defect.

## Assurance boundary

- Financial owner/external pointer consistency: `REPAIRED_AND_REREAD`
- duplicate active Library routing: `CLEANED`
- Google Drive active Financial authority conflict: `NOT_FOUND_IN_CHECKED_ACTIVE_ROUTING`
- owner full hosted CI: `OPEN__RUNNER_NOT_EXECUTED`
- real post-rebuild article E2E: `OPEN`
- post-rebuild live writing quality: `OPEN`
- generic new-chat automatic Financial discovery: `OPEN__REAL_PRODUCT_TRACE_REQUIRED`
