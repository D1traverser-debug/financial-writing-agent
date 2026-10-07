# Phase-1 status

**Private Site compatibility PoC — NOT production-ready. Do not publish or share.**

Implemented in this layer:

- Site-native D1/R2 bindings (`DB`, `FILES`).
- D1 checkpoint CAS with `checkpoint_version` optimistic concurrency and stale-write rejection.
- R2 object identity with SHA-256 write/readback verification.
- Frozen 16-tool MCP contract snapshot plus the four existing resource URI templates.
- State transition table, BLOCKED origin/resume, revision invalidation, mandatory completion-gate inventory, and WritingAcceptanceContract freezing ported from the Python behavioral oracle.
- Explicit Python deterministic-delivery/render compatibility bridge boundary.

Not implemented or promoted in Phase 1:

- Site-native DOCX generation.
- Site-native Word mechanical QA.
- Site-native LibreOffice/Poppler rendering.
- Full business execution wiring for all 16 tools. The MCP surface is exposed from the frozen snapshot, but tool execution fails closed until parity wiring is complete; no free-form fallback exists.
- Fresh-chat / runtime-restart persistence proof on deployed Site infrastructure.
- Real-article live-model E2E. Current production-promotion count remains 0.
