# Financial Writing Agent Runtime — Site migration PoC

Private compatibility layer for `D1traverser-debug/financial-writing-agent` branch `v0.2.1-runtime-rule-hardening`.

This directory does **not** replace the Python runtime and must not be treated as production-ready. The existing Python implementation remains the behavioral oracle. DOCX construction, Word mechanical QA, LibreOffice rendering, and Poppler page rendering remain behind the explicit Python deterministic-delivery compatibility bridge during Phase 1.

Site bindings: D1 `DB`, R2 `FILES`. Do not publish or share during this PoC.
