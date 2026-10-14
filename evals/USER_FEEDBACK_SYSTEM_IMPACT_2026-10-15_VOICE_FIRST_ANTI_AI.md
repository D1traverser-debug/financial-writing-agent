# User Feedback System Impact — Voice-First Anti-AI Calibration

Date: 2026-10-15
Owner: `DOMAIN:financial_writing`
Trigger: user challenged the first post-0.9.0 anti-AI explanation itself as still AI-shaped and explicitly asked to use the parent cognition/evolution system to challenge the first idea before adding rules.

## Observed failure

The 0.9.0 direction correctly moved beyond synonym replacement, but the explanation and rule surface still over-generalized corpus-level AI/human differences into generation-time prescriptions. In practice this can replace one machine template with another: `different paragraph roles`, `verdict -> evidence -> boundary`, forced rhetorical variation, or platform-casual phrases can themselves become repeated scaffolds.

## Parent cognition pass

### Micro diagnosis
- The assistant responded to an aesthetic/authorial problem by enumerating a rule list.
- The response itself repeated the same explanatory move it warned against: definition -> numbered symptoms -> preferred replacement formula.
- Therefore passing the existing anti-template checklist is not sufficient evidence of human/authorial prose.

### Macro goal
The product goal is not to make text statistically unlike AI. It is to publish finance writing that sounds like a situated author with a real reader, real evidence, real selection pressure, and a defensible point of view.

### Governing assumption challenged
Rejected assumption: group-level stylometric differences can be translated directly into universal per-article generation rules.

Replacement assumption: anti-AI indicators are mostly **diagnostic signals**. Generation should be conditioned first on audience, purpose, audited material, author stance, and—when available—the user's own approved writing samples. A working passage should not be rewritten merely to satisfy a stylistic quota.

## External research and practitioner evidence

1. ACL 2026, *Can You Make It Sound Like You? Post-Editing LLM-Generated Text for Personal Style* (Baumler et al.). Post-editing moves drafts toward users' style but the outputs remain closer to LLM text and show less stylistic diversity than unassisted human writing. This weakens the strategy `generic AI draft -> humanizer cleanup`.
2. 2025 IEEE UEMCON, *How Well Do LLMs Imitate Human Writing Style?* Few-shot/completion prompting had much larger style-fidelity effects than model size in the reported experiments. This supports using owned voice samples rather than generic 'sound human' adjectives.
3. `smillunchick/writing-skill`: human substance before prose; genre-specific constraints; multiple distinct candidates; best-parts synthesis; span-level editing; preserve useful roughness; optimize for reader trust rather than detector scores.
4. `GuMu599/human-writing-skill`: diagnose information/structure/scene/wording before editing; keep an information ledger; require a material threshold for long-form writing; treat AI signals as clustered symptoms rather than single-token bans; do not rewrite functioning elements merely to satisfy a mode word.
5. `zdyya/writer-skill`: useful positive pattern is user-owned style samples plus separated Reader / Editor / Style-Coach review passes. Negative pattern: its optional strict-human mode also demonstrates the danger of quotas (required casual phrases, punctuation bans, required cultural metaphor/callback), which can become a new template.
6. `JIAXInT/xhs-content-generator`: useful negative case. '极度口语化' plus fixed phrases such as `说真的/真的绝了/你说是不是` shows how de-AI rules can collapse into a platform caricature.
7. Public Xiaohongshu-oriented practitioner material converges on a useful warning: blindly splitting sentences, injecting emotion words, perfecting symmetric lists, or forcing interaction prompts can produce another standardized voice. More robust advice emphasizes concrete actions/context and real material rather than a magic prompt.

## Alternatives compared

### A. Add more anti-AI bans and quotas
Mechanism: expand phrase blacklists, sentence-length targets, rhetorical-role variation and platform-specific casual-language requirements.
Failure mode: directly reproduces the user's complaint—another higher-order template. Reject.

### B. Voice/material first; anti-AI diagnosis after drafting
Mechanism: before drafting, bind audience/purpose/evidence/author stance and use user-approved voice samples when available; for substantive long-form work explore structurally distinct candidate openings/section paths; after drafting run separate Reader, Editor and Style diagnostic passes. AI-tell heuristics are warnings, not generation mandates. Revise only the spans that actually fail reader/voice/information tests.
Failure mode: requires enough real material and, for strong voice matching, enough approved user writing. Mitigation: when samples are absent, use platform/genre conventions but do not invent personal experience.
Selected.

### C. Generic draft then humanizer post-pass
Mechanism: draft normally and run one de-AI rewrite at the end.
Failure mode: post-editing can retain LLM stylistic residue and may flatten distinctive content/voice. Reject as primary strategy; retain only targeted span repair.

## Product changes admitted

1. Reclassify anti-AI pattern checks as **diagnostic/audit signals**, except separately justified hard publication/compliance gates.
2. Add a voice-evidence hierarchy: user-approved/edited samples > current user's explicit style constraints and prose signals > target platform/genre conventions > generic defaults.
3. Never fabricate personal experiences or 'human details' to create authenticity.
4. Keep title/opening/company-comparison reader-value requirements, but forbid one-to-one sentence formulas or universal rhetorical shells.
5. `verdict -> evidence -> boundary` becomes one useful comparison pattern, not a mandatory prose order.
6. Use the existing `DRAFT -> EDITORIAL_AUDIT` workflow for separated writer/reader/editor/style passes; do not create a new controller or workflow stage. Same-model passes are critique/candidate evidence, not independent certification.
7. Prefer minimum effective revision: if a passage is specific, situated, clear and voice-consistent, do not change it solely because it contains a commonly flagged construction once.
8. For substantial long-form writing, compare at least two genuinely different opening/section strategies before finalizing; do not count synonym variants as alternatives.

## Evaluation plan

Regression tests must prove:
- one isolated `不是X而是Y`-type construction is not a failure by itself;
- clustered scaffolding can still trigger revision;
- current policy declares AI-pattern signals diagnostic rather than generation mandates;
- voice-source priority favors user-owned approved samples;
- same-model reader/editor/style passes are explicitly non-independent;
- package/version/documentation remain coherent.

Post-promotion live observation remains required on the next real finance article. The decisive evidence is whether the article reads less like a rule-compliant standard answer without losing factual density, company differentiation, hook quality or compliance.
