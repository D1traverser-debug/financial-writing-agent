from financial_writing_agent.models import TaskContract, WritingState
from financial_writing_agent.store import SQLiteStateStore


def _state(sample_type: str) -> WritingState:
    state = WritingState(contract=TaskContract(task_id=f"persist-{sample_type.lower()}", prompt="test"))
    state.working["learning_samples"] = [
        {
            "sample_type": sample_type,
            "summary": "material feedback",
            "source_refs": ["evidence://user-feedback"],
            "promotion_status": "RAW_EVIDENCE_ONLY",
        }
    ]
    return state


def test_negative_feedback_is_never_first_persisted_without_impact_obligation(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    state = _state("USER_REJECTION")
    store.save(state)

    loaded = store.load(state.contract.task_id)
    assert loaded is not None
    sample = loaded.working["learning_samples"][0]
    signal_id = sample["system_impact_signal_id"]
    signals = loaded.working["system_impact_signals"]
    assert len(signals) == 1
    assert signals[0]["signal_id"] == signal_id
    assert signals[0]["status"] == "PENDING_REVIEW"


def test_non_negative_learning_evidence_does_not_create_impact_obligation(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    state = _state("USER_ACCEPTANCE")
    store.save(state)

    loaded = store.load(state.contract.task_id)
    assert loaded is not None
    assert "system_impact_signal_id" not in loaded.working["learning_samples"][0]
    assert loaded.working.get("system_impact_signals", []) == []


def test_repeated_save_is_idempotent_for_impact_signal(tmp_path):
    store = SQLiteStateStore(tmp_path / "state.db")
    state = _state("USER_FEEDBACK")
    store.save(state)
    store.save(state)

    loaded = store.load(state.contract.task_id)
    assert loaded is not None
    assert len(loaded.working["system_impact_signals"]) == 1
