# Financial Writing Agent — standalone

**Operating owner:** this repository, D1traverser-debug/financial-writing-agent@main. **Runtime:** direct Financial Writing Skill and owner-native article state. **External parent required:** NO.

This system independently owns the full Chinese/A-share financial content lifecycle: source discovery and evidence, economic company-universe research, private analytical briefs, competing thesis decisions, two independently designed Deep/Broad articles, platform posts, originality and fact review, actual Word creation, render/visual inspection, user-visible delivery and feedback-driven improvement.

## Entry for a connected ChatGPT/Work session

1. Connect/select **Financial Writing** itself, not CAOS, UAOS or their Host. The live operating skill is [skills/financial-writing-agent/SKILL.md](skills/financial-writing-agent/SKILL.md); [FINANCIAL_SKILL.md](FINANCIAL_SKILL.md) is its root discovery index.
2. The native independent manifest is [config/FINANCIAL_MANIFEST.json](config/FINANCIAL_MANIFEST.json) and capability declaration is [config/FINANCIAL_CAPABILITIES.json](config/FINANCIAL_CAPABILITIES.json). The only business state is per-article [workspaces/articles](workspaces/articles) STATE.json, validated by [current_admission.py](financial_writing_agent/current_admission.py).
3. For actual authorized GitHub state writes, a connected implementation can call [standalone_runtime.py](financial_writing_agent/standalone_runtime.py): user-scoped permission verifier, exact source-byte read, compare-and-swap Git write, and second readback. The caller must genuinely connect these capabilities; this repository is **not itself a deployed app server**.
4. The old .uaos/*, CAOS_SKILL.md, UAOS_SKILL.md, the historical CAOS child interface and previous governance experiments are **inactive history**, not required for direct operation.

No CAOS repository modification, clone or runtime dependency is needed. No subscription to another provider is implied. A live language model/web source and user-authorized Git connection are required for corresponding live tasks, and a DOCX renderer for page QA.

## Financial business workflow

INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT.

Financial's own decision loop recovers the owner's actual goal, compares evidence and falsifiers, chooses the best suited method. Its execution loop performs the work, verifies exact effects, repairs the shared cause and checks meaningful output. The single guarded provider port now also routes blocked-review recovery, proactive resolution and feedback impact review through the same Financial article state; illegal failure cursors are rejected. The internal [writing kernel](financial_writing_agent/writing_kernel.py) and [decision envelope](financial_writing_agent/cognition_governance.py) specialize those methods for finance; they are NOT an external parent controller.

For a normal portfolio, target deliverables are actual **FINANCE_DEEP_DOCX, FINANCE_BROAD_DOCX, PLATFORM_INTERACTION_PACK_DOCX and AUDIT_DOCX**. PrivateResearchBrief 1.1 with 15 modules is admitted prior to thesis. Deep usually selects useful arguments from comprehensive private work; the active cross-border article has an explicit **full retained company universe in Deep** exception. Keep current task requirements, company comparisons and source/Word receipts bound to the article revision. Broad must be independently planned rather than a shortened Deep.

## Current Financial-only production gates (2026-11-12)

The authentic frozen cross-border v3 retained pool has **174 ticker IDs**, now packaged as `resources/task_universe_baselines.json` and reconciled before the source stage transitions. A current research advance through the independent provider adapter now needs a real `source_snapshot_reader` returning `text`, `sha256`, `retrieved_at` and `source_family` for **each** of the fifteen private-research modules' evidence refs. Stale briefs, unread sources and single-family self-support no longer pass the high-level research port. This still does not verify underlying financial truth.

The publication source trace now rejects conservative gross contradictions (growth vs decline, reporting period, unit/metric direction) before issuing a numerical trace receipt, while **semantic entailment remains unverified**. The existing user-specific full-retained universe is checked against authentic ticker identity, not merely the count submitted by the model.

At the same Financial provider action boundary, entering DELIVERY and passing FINAL_AUDIT also require actual article-scoped Word binary readback for the full output portfolio; nonexistent files and metadata-only hashes cannot mutate the article to a delivered state. This binary gate does not certify per-page QA or content quality.

Independent editorial review is supportable only with authenticated provider verification, a different reviewer, and exact DRAFT bytes/content hash and attestation. Self-review remains self-review. The current visible Word delivery additionally requires real binary readback and verified per-page render receipt across **all four required Word types**. These checks do not constitute reader acceptance.

See [the exact main-only repair and operating contract](docs/FINANCIAL_MAIN_ONLY_REPAIR_AND_RUNTIME_20261112.md). **No installed Financial ChatGPT connector or source-verified current cross-border article is implied by a green CI.**

## Run the engineering checks

```bash
python -m pip install -e '.[dev]'
coverage run --source=financial_writing_agent -m pytest -q
coverage report -m
python scripts/eval_contracts.py
python scripts/static_audit.py
python scripts/retired_runtime_static_audit.py
python scripts/whole_tree_audit.py
```

CI additionally builds an isolated wheel and actually renders Word pages. **Engineering PASS is not factual, editorial or reader acceptance.** See [evals/EVOLUTION_INDEX.json](evals/EVOLUTION_INDEX.json) for domain-system readiness. The current cross-border v3 remains RESEARCH until a genuine current source-verified trajectory advances it. Financial works without CAOS, but no live independent end-to-end editorial success is claimed from unit tests.
