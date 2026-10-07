import json
from pathlib import Path


def test_unique_rule_ownership():
    data = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    seen = set()
    for _, keys in data.items():
        for key in keys:
            assert key not in seen, key
            seen.add(key)


def test_visual_workflow_is_explicit_and_owned():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    assert "visuals" in ownership
    assert "visual_planning" in ownership["visuals"]
    assert Path("references/visuals.md").is_file()
    assert not Path("SKILL.md").exists()

    skill = Path("skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    public_server = Path("financial_writing_agent/plugin_server.py").read_text(encoding="utf-8")
    runtime = Path("financial_writing_agent/runtime_service.py").read_text(encoding="utf-8")
    shim = Path("financial_writing_agent/mcp_server.py").read_text(encoding="utf-8")

    assert "references/visuals.md" in skill
    assert "submit_visual_package" in skill
    assert "submit_visual_package" in public_server
    assert "submit_visual_package" in runtime
    assert 'openai/fileParams' in public_server
    assert "@mcp.tool" not in runtime
    assert "@mcp.tool" not in shim
    assert "from .plugin_server import main, mcp" in shim


def test_mcp_entry_requires_explicit_continuation_before_task_restore():
    public_server = Path("financial_writing_agent/plugin_server.py").read_text(encoding="utf-8")
    assert "Resume unfinished tasks before starting new ones." not in public_server
    assert "Only explicit continuation intent may restore an unfinished task" in public_server
    assert "a new task must start fresh even when unfinished tasks exist" in public_server


def test_research_harness_and_effective_time_boundary_are_wired_end_to_end():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    models = Path("financial_writing_agent/models.py").read_text(encoding="utf-8")
    routing = Path("financial_writing_agent/routing.py").read_text(encoding="utf-8")
    runtime = Path("financial_writing_agent/runtime_service.py").read_text(encoding="utf-8")
    public_server = Path("financial_writing_agent/plugin_server.py").read_text(encoding="utf-8")
    public_contracts = Path("financial_writing_agent/mcp_contracts.py").read_text(encoding="utf-8")
    research = Path("references/research.md").read_text(encoding="utf-8")
    audit = Path("references/audit.md").read_text(encoding="utf-8")

    assert "effective_time_boundary" in ownership["runtime"]
    assert "effective_time_boundary: datetime" in models
    assert "effective_time_boundary: datetime | None = None" in routing
    assert "validate_research_against_knowledge_context" in runtime
    assert "harness_evidence = validate_research_against_knowledge_context(state, payload)" in runtime
    assert 'f"effective_time_boundary={state.contract.effective_time_boundary.isoformat()}"' in runtime
    assert "GLOBAL.time_integrity must quote the exact frozen effective_time_boundary=" in runtime
    assert "effective_time_boundary: datetime" in public_contracts
    assert "effective_time_boundary:" in public_server
    assert "effective_time_boundary=effective_time_boundary" in public_server
    assert "TaskContract.effective_time_boundary" in research
    assert "GLOBAL.time_integrity` must quote the persisted task's exact `TaskContract.effective_time_boundary`" in audit


def test_maintenance_requires_executable_low_judgment_rules_and_canonical_identity():
    ownership = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    maintenance = Path("references/maintenance.md").read_text(encoding="utf-8")

    assert "mechanically_decidable_rule_enforcement" in ownership["maintenance"]
    assert "canonical_system_document_identity" in ownership["maintenance"]
    assert "not migrated merely because prose was updated" in maintenance
    assert "schema/gate/check assertion and a recurrence test" in maintenance
    assert "Canonical system-document identity" in maintenance
    assert "displayed title plus provider identity" in maintenance


def test_legacy_cold_start_editorial_and_platform_semantics_remain_present():
    editorial = Path("references/editorial.md").read_text(encoding="utf-8")
    platforms = Path("references/platforms.md").read_text(encoding="utf-8")

    # Legacy T06: generate from current TopicDNA before recent-outline collision checks.
    assert "Candidate structures must be generated from the current TopicDNA before recent-outline fingerprints are consulted" in editorial
    assert "collision checks, never structure-generation inputs" in editorial

    # Legacy T07: no fixed event/industry/stocks/market/next-stage template.
    assert "A fixed “event → industry → stocks → market → next stage” skeleton is not a default" in editorial

    # Legacy T09: broad distribution remains financial and cross-sector understandable.
    assert "finance readers outside the sector understand investment relevance" in platforms
    assert "Lower entry cost without deleting the strongest contradiction or the core causal chain" in platforms

    # Legacy T10: only load current platform/account experience for relevant optimization work.
    assert "recommendation, click-through, search, retention or account-specific performance" in platforms
    assert "retrieve the **current relevant version**" in platforms
    assert "Do not promote it to a permanent formula without repeated, comparable evidence" in platforms

    # Legacy T13: compress redundancy before reasoning/evidence.
    assert "Compress repeated explanation, textbook background, synonym restatement" in editorial
    assert "counterexamples, why-this/why-not, market-selection mechanism" in editorial
