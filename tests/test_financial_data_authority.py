"""The Financial data authority has one canonical path for every persistent asset."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_data_authority_has_one_business_state_and_method_store():
    data=json.loads((ROOT/"config/DATA_AUTHORITY.json").read_text(encoding="utf-8"))
    manifest=json.loads((ROOT/"config/FINANCIAL_MANIFEST.json").read_text(encoding="utf-8"))
    assert data["domain_id"]==manifest["domain_id"]=="financial_writing"
    assert data["business_authority"]=="github://D1traverser-debug/financial-writing-agent@main"
    assert data["article_state_pattern"]==manifest["state_authority"]
    assert data["method_catalog"]=="knowledge/METHOD_KNOWLEDGE_CATALOG.json"
    assert data["system_evolution"]=="evals/EVOLUTION_INDEX.json"
    assert data["no_parallel_article_ledger"] is True
    assert data["no_external_parent_runtime"] is True

def test_article_crud_is_task_scoped_and_history_is_preserved():
    data=json.loads((ROOT/"config/DATA_AUTHORITY.json").read_text(encoding="utf-8"))
    assert data["article_workspace"]["state"]=="STATE.json"
    assert set(data["article_workspace"])=={"state","research","editorial","stage_outputs","reviews","delivery","feedback"}
    assert "append-only history" in data["operations"]["update"]
    assert "Do not erase historical receipts" in data["operations"]["delete"]
    assert "actual DOCX" in data["operations"]["delivery"]
