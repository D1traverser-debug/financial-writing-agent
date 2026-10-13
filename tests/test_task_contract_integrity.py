import pytest
from pydantic import ValidationError

from financial_writing_agent.models import ArtifactKind, DistributionMode, TaskContract
from financial_writing_agent.routing import build_task_contract


def _values(contract: TaskContract) -> list[str]:
    return [kind.value for kind in contract.required_outputs]


def test_routing_still_derives_default_dual_outputs():
    contract = build_task_contract(prompt="test")
    assert contract.distribution_mode == DistributionMode.DUAL
    assert _values(contract) == [
        ArtifactKind.AUDIT_DOCX.value,
        ArtifactKind.FINANCE_DEEP_DOCX.value,
        ArtifactKind.FINANCE_BROAD_DOCX.value,
    ]


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        (
            DistributionMode.DUAL,
            [ArtifactKind.AUDIT_DOCX, ArtifactKind.FINANCE_DEEP_DOCX, ArtifactKind.FINANCE_BROAD_DOCX],
        ),
        (
            DistributionMode.FINANCE_DEEP,
            [ArtifactKind.AUDIT_DOCX, ArtifactKind.FINANCE_DEEP_DOCX],
        ),
        (
            DistributionMode.FINANCE_BROAD,
            [ArtifactKind.AUDIT_DOCX, ArtifactKind.FINANCE_BROAD_DOCX],
        ),
    ],
)
def test_exact_explicit_required_outputs_are_accepted(mode, expected):
    contract = TaskContract(prompt="test", distribution_mode=mode, required_outputs=expected)
    assert contract.required_outputs == expected


@pytest.mark.parametrize(
    ("mode", "bad_outputs"),
    [
        (DistributionMode.DUAL, [ArtifactKind.AUDIT_DOCX, ArtifactKind.FINANCE_BROAD_DOCX]),
        (DistributionMode.DUAL, [ArtifactKind.AUDIT_DOCX, ArtifactKind.FINANCE_DEEP_DOCX]),
        (DistributionMode.FINANCE_DEEP, [ArtifactKind.AUDIT_DOCX]),
        (DistributionMode.FINANCE_BROAD, [ArtifactKind.AUDIT_DOCX, ArtifactKind.FINANCE_DEEP_DOCX]),
    ],
)
def test_nonempty_mismatched_required_outputs_fail_closed(mode, bad_outputs):
    with pytest.raises(ValidationError, match="required_outputs must exactly match"):
        TaskContract(prompt="test", distribution_mode=mode, required_outputs=bad_outputs)
