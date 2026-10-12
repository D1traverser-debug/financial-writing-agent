# Financial Writing Fresh-Chat / External Authority Audit — 2026-10-12

Status: OPEN

Purpose: verify that a new ChatGPT conversation can route a normal financial-writing request to the current Financial owner without depending on stale chat memory, stale Library/Notion pointers, or obsolete execution modes.

Confirmed findings before repair:

1. `continuity/tasks/financial-writing-main/TASK_MANIFEST.json` still referenced execution capability profile 9 in `next_action` while `continuity/EXECUTION_CAPABILITIES.json` is profile 10.
2. `continuity/tasks/financial-writing-main/HANDOFF.md` still described the older owner-native-only/Standalone-era state and did not describe the current GITHUB_CHAT adapter, Phase-1 canonical workflow kernel, or Phase-2 checkpoint CAS/recovery semantics.
3. ChatGPT Library `/A股超短系统/00_写作Agent_新对话恢复入口.md` still pointed to `v0.2.1-writing-agent-integrated` and the retired `STANDALONE_SKILL/ShadowTaskLedger` fallback.
4. ChatGPT Library contained a second older root-level `00_A股系统_新对话接班指引.md` duplicate in addition to the current `/A股超短系统/...` copy.
5. Notion `A股超短系统｜知识导航（非全局恢复入口）` still copied the old Financial branch/Standalone routing text.
6. Google Drive `00_ROUTER_系统入口与任务路由` already declares Financial GitHub `main` as the sole writing execution/rule authority and constrains Drive/Notion to reference/knowledge roles; Drive search found no `v0.2.1-writing-agent-integrated` occurrence.

Boundary:
- GitHub `main` remains Financial engineering/rule authority.
- External stores are reference/bootstrap surfaces only and must not contain a competing execution mode.
- Updating external pointers does not itself prove that ChatGPT product routing will automatically read them in every brand-new chat. Guaranteed zero-prompt bootstrap requires an actually always-on account/product routing hook; that is a separate product-capability boundary from owner correctness.

Planned repair:
- reconcile Financial task continuity to profile 10 and current GITHUB_CHAT/owner-native architecture;
- replace stale Library Financial recovery pointer text with current `main` + GITHUB_CHAT semantics;
- remove the redundant older root-level A-share handoff duplicate while preserving the current scoped copy;
- update Notion navigation copy to point to GitHub `main` + current execution handshake and remove Standalone/ShadowTaskLedger routing;
- re-read all mutated surfaces and verify no stale branch/Standalone terms remain in active pointers.
