# Financial Writing — standalone ChatGPT/Work or plugin deployment

This is a **Financial-only** capability transport. There is no CAOS/UAOS parent, external controller, parent grant or local Host dependency.

Canonical operating skill: skills/financial-writing-agent/SKILL.md. Domain config: config/FINANCIAL_MANIFEST.json and config/FINANCIAL_CAPABILITIES.json. Business owner: financial_writing_agent.current_admission. Provider-neutral action port: financial_writing_agent.standalone_runtime.

A connected app binds its genuinely authenticated GitHub reads/conditional writes and an external user-authorization verifier. The action port accepts create, requirements, advance and user-feedback operations, checks expected Git Blob SHA, verifies stage artifact bytes where needed, writes through Financial's current owner and independently reads it back. Read-only article status does not imply permission to write. No client-supplied permission flag, fake callback, unverified write response or same-model review can be treated as a native host grant.

LLM/agent execution and web/filing retrieval belong to the connected Financial client; our domain DecisionEnvelope, research, story, audit and delivery policies own the writing decisions. An LLM invocation is never simulated by a passing Python test. For Word output use the actual DOCX binary and render/visual/source proof, with accessible links.

Do not enable public multi-user deployment until real authentication, tenant isolation, secrets separation, audit logs, budget limits, source rights, malicious-source handling and cross-user tests are in place. CI proves domain code only; the live plugin/service installation, app authentication and independently judged reader quality remain separate user-acceptance gates.

No active runtime depends on any file or executable from cognition-agent-os.
