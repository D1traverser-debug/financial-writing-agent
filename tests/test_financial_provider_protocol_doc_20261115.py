import inspect
from pathlib import Path

from financial_writing_agent import portfolio_coordinator, provider_attestation, standalone_runtime


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs" / "FINANCIAL_PROVIDER_ACTION_PROTOCOL_V1_20261115.md"


def test_provider_protocol_is_explicitly_draft_and_not_deployed():
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "DRAFT CONTRACT — NOT DEPLOYED" in text
    assert "MCP Streamable HTTP over HTTPS" in text
    assert "does not create a second business controller" in text
    assert "the ChatGPT model remains responsible for semantic research" in text


def test_protocol_uses_existing_attestation_trust_domain_not_model_supplied_identity():
    text = PROTOCOL.read_text(encoding="utf-8")
    for value in (
        provider_attestation.AUDIENCE,
        provider_attestation.KEY_ENV,
        provider_attestation.PROVIDER_ENV,
        provider_attestation.OWNER_ENV,
    ):
        assert value in text
    assert "never trust an actor ID" in text
    assert "model tool arguments" in text


def test_protocol_entrypoints_match_existing_python_runtime_contracts():
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "standalone_runtime.observe_article" in text
    assert "standalone_runtime.admit_article_action" in text
    assert "standalone_runtime.observe_method_catalog" in text
    assert "standalone_runtime.admit_method_action" in text
    assert "portfolio_coordinator.run_next_portfolio_stage" in text

    article = inspect.signature(standalone_runtime.admit_article_action).parameters
    assert {"state_reader", "authorization_verifier", "bundle_cas_writer",
            "effect_attestation_signer", "effect_receipt_reader"} <= set(article)
    method = inspect.signature(standalone_runtime.admit_method_action).parameters
    assert {"catalog_reader", "authorization_verifier", "catalog_bundle_cas_writer",
            "effect_attestation_signer", "effect_receipt_reader"} <= set(method)
    stage = inspect.signature(portfolio_coordinator.run_next_portfolio_stage).parameters
    assert {"execute_pass", "research_audit", "state_reader",
            "artifact_bundle_writer", "authorization_verifier",
            "bundle_cas_writer", "effect_attestation_signer"} <= set(stage)


def test_protocol_requires_separate_owner_and_independent_reviewer_trust_domains():
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "FINANCIAL_METHOD_REVIEW_KEY" in text
    assert "FINANCIAL_METHOD_REVIEW_PROVIDER_ID" in text
    assert "owner Provider Action cannot supply the independent method-review attestation" in text
    assert "owner_change_approval" in text or "owner_change" in text
