import hashlib
import json
from pathlib import Path

from financial_writing_agent.current_admission import validate_state


ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v2"
V3 = ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v3"


def _digest(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_current_successor_is_owner_native_and_requirement_bound():
    state = json.loads((V3 / "STATE.json").read_text(encoding="utf-8"))
    validate_state(state)

    assert state["task_id"] == "cross-border-ecommerce-20261016-v3"
    assert state["writing_kernel_version"] == "1.0"
    assert state["task_requirement_contract_version"] == "1.0"
    authority = state["task_requirement_authority"]
    assert authority["revision"] == 1
    assert state["task_requirement_digest"] == _digest(authority)
    assert {item["requirement_id"] for item in authority["active_requirements"]} == {
        "full_universe_research_pool",
        "deep_complete_retained_universe",
    }
    latest = state["execution_receipts"][-1]["input_bindings"]
    assert latest["task_requirement_revision"] == 1
    assert latest["task_requirement_digest"] == state["task_requirement_digest"]
    assert latest["task_requirement_authority_path"] == "financial_writing_agent.task_requirements"


def test_v2_namespace_is_explicitly_migrated_history_with_no_current_artifacts():
    manifest = json.loads((V2 / "ARTIFACT_STATUS.json").read_text(encoding="utf-8"))
    assert manifest["workspace_lifecycle"] == "MIGRATED_HISTORY"
    assert manifest["successor_task_id"] == "cross-border-ecommerce-20261016-v3"
    assert manifest["current_authority"] == "workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json"
    statuses = manifest["statuses"]
    assert statuses
    assert "KEEP_CURRENT" not in statuses.values()
    assert all(status in set(manifest["allowed_statuses"]) for status in statuses.values())
    for relative_path in statuses:
        assert (V2 / relative_path).exists(), relative_path

    # Collision-prone generations must be explicitly historical rather than active-looking.
    for relative_path in (
        "stages/DRAFT.md",
        "stages/DRAFT_V2_20261016.md",
        "stages/TITLE.md",
        "stages/TITLE_V2_20261016.md",
        "reviews/EDITORIAL_AUDIT.md",
        "reviews/EDITORIAL_AUDIT_REV1.md",
        "reviews/EDITORIAL_AUDIT_RECOVERY_20261016.md",
        "reviews/PUBLICATION_FITNESS.json",
        "reviews/PUBLICATION_FITNESS_REV1.json",
        "reviews/PUBLICATION_FITNESS_RECOVERY_20261016.json",
        "delivery/FULL_UNIVERSE_VISIBLE_DELIVERY_20261016.json",
        "delivery/PRIVATE_RESEARCH_SHORT_TERM_UPGRADE_20261016.json",
        "delivery/VISIBLE_DELIVERY_RECOVERY_20261016.json",
        "delivery/WORD_DELIVERY_CANDIDATE_20261016.json",
    ):
        assert statuses[relative_path] == "ARCHIVE_PROVENANCE"
