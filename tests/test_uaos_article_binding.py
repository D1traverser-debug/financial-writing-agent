import pytest

from financial_writing_agent.uaos_binding import (
    UaosArticleBindingError,
    expected_article_state_path,
    expected_business_authority,
    expected_uaos_task_state_ref,
    validate_uaos_article_binding,
)


def _uaos(task_id="financial-writing:article-1", **overrides):
    data = {
        "task_id": task_id,
        "domain_id": "financial_writing",
        "task_type": "article",
        "domain_business_authority": expected_business_authority(task_id),
    }
    data.update(overrides)
    return data


def _state(task_id="financial-writing:article-1", **overrides):
    data = {"schema_version": "1.2", "task_id": task_id, "state_ref": "main"}
    data.update(overrides)
    return data


def test_expected_refs_share_one_task_identity():
    task_id = "financial-writing:article-1"
    assert expected_article_state_path(task_id) == f"workspaces/articles/{task_id}/STATE.json"
    assert expected_uaos_task_state_ref(task_id) == f"state/tasks/{task_id}.json"
    assert expected_business_authority(task_id).endswith(expected_article_state_path(task_id))


def test_valid_uaos_article_binding_passes():
    validate_uaos_article_binding(_uaos(), _state())


def test_task_id_mismatch_fails_closed():
    with pytest.raises(UaosArticleBindingError, match="task_id"):
        validate_uaos_article_binding(_uaos(), _state("financial-writing:other"))


def test_wrong_domain_or_business_authority_fails_closed():
    with pytest.raises(UaosArticleBindingError, match="financial_writing"):
        validate_uaos_article_binding(_uaos(domain_id="video"), _state())
    with pytest.raises(UaosArticleBindingError, match="domain_business_authority"):
        validate_uaos_article_binding(_uaos(domain_business_authority="wrong"), _state())


def test_router_cannot_masquerade_as_article_task():
    with pytest.raises(UaosArticleBindingError, match="router"):
        validate_uaos_article_binding(
            _uaos("financial-writing:main", task_type="article_workspace_router"),
            _state("financial-writing:main"),
        )


def test_explicit_historical_state_can_be_adopted_without_receipt_rewrite():
    historical = {"schema_version": "1.1", "task_id": "ice-snow-economy-20261013"}
    uaos = _uaos("ice-snow-economy-20261013")
    validate_uaos_article_binding(uaos, historical)


def test_non_main_current_state_ref_fails_closed():
    with pytest.raises(UaosArticleBindingError, match="state_ref"):
        validate_uaos_article_binding(_uaos(), _state(state_ref="feature"))


def test_unsafe_workspace_task_id_is_rejected():
    with pytest.raises(UaosArticleBindingError, match="safe"):
        expected_article_state_path("../escape")
