import pytest

from financial_writing_agent.plugin_server import _reject_unverified_semantic_pass


def test_chat_bridged_semantic_pass_is_rejected():
    with pytest.raises(ValueError, match="run_semantic_audit_stage"):
        _reject_unverified_semantic_pass("PASS", "research_audit")


def test_conservative_nonpass_audit_input_remains_allowed():
    _reject_unverified_semantic_pass("REVISE", "research_audit")
    _reject_unverified_semantic_pass("FAIL", "final_audit")
