from __future__ import annotations

from collections.abc import Mapping

FINANCIAL_DOMAIN_ID = "financial_writing"
FINANCIAL_REPOSITORY = "D1traverser-debug/financial-writing-agent"
FINANCIAL_ROUTER_TASK_ID = "financial-writing:main"


class UaosArticleBindingError(ValueError):
    """Raised when UAOS controller identity and Financial article state diverge."""


def _task_id(value: object) -> str:
    task_id = str(value or "").strip()
    if not task_id:
        raise UaosArticleBindingError("article task_id is required")
    if "/" in task_id or "\\" in task_id or ".." in task_id:
        raise UaosArticleBindingError("article task_id is not safe for the canonical workspace path")
    return task_id


def expected_article_state_path(task_id: str) -> str:
    clean = _task_id(task_id)
    return f"workspaces/articles/{clean}/STATE.json"


def expected_business_authority(task_id: str) -> str:
    return f"{FINANCIAL_REPOSITORY}@main:{expected_article_state_path(task_id)}"


def expected_uaos_task_state_ref(task_id: str) -> str:
    clean = _task_id(task_id)
    return f"state/tasks/{clean}.json"


def validate_uaos_article_binding(
    uaos_task: Mapping[str, object], article_state: Mapping[str, object]
) -> None:
    """Validate the one-to-one controller/business-state identity contract.

    This does not create controller state and is not a second registry. UAOS owns the
    durable task; the Financial repository owns the article state. The shared task_id
    plus the exact domain_business_authority joins those two authorities.

    Historical schema-1.1 article states may not contain ``state_ref``. They can be
    explicitly adopted by a current UAOS article task without rewriting immutable
    historical receipts. New/current states that expose ``state_ref`` must bind main.
    """

    uaos_task_id = _task_id(uaos_task.get("task_id"))
    article_task_id = _task_id(article_state.get("task_id"))
    if uaos_task_id == FINANCIAL_ROUTER_TASK_ID:
        raise UaosArticleBindingError("the Financial router task is not an article task")
    if uaos_task_id != article_task_id:
        raise UaosArticleBindingError("UAOS task_id must equal Financial article STATE.task_id")

    domain_id = str(uaos_task.get("domain_id") or uaos_task.get("owner_domain") or "").strip()
    if domain_id != FINANCIAL_DOMAIN_ID:
        raise UaosArticleBindingError("UAOS article task must belong to financial_writing")

    task_type = str(uaos_task.get("task_type") or "article").strip()
    if task_type != "article":
        raise UaosArticleBindingError("UAOS Financial material task must use task_type=article")

    expected_authority = expected_business_authority(uaos_task_id)
    actual_authority = str(uaos_task.get("domain_business_authority") or "").strip()
    if actual_authority != expected_authority:
        raise UaosArticleBindingError(
            "UAOS domain_business_authority must point to the exact Financial article STATE"
        )

    state_ref = article_state.get("state_ref")
    if state_ref is not None and str(state_ref).strip() != "main":
        raise UaosArticleBindingError("Financial article state_ref must be main when present")
