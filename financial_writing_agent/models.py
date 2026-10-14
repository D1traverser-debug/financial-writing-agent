from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Stage(str, Enum):
    INTAKE = "INTAKE"
    RESEARCH = "RESEARCH"
    RESEARCH_AUDIT = "RESEARCH_AUDIT"
    EDITORIAL = "EDITORIAL"
    TITLE = "TITLE"
    DRAFT = "DRAFT"
    EDITORIAL_AUDIT = "EDITORIAL_AUDIT"
    DELIVERY = "DELIVERY"
    MECHANICAL_AUDIT = "MECHANICAL_AUDIT"
    FINAL_AUDIT = "FINAL_AUDIT"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class DistributionMode(str, Enum):
    FINANCE_DEEP = "FINANCE_DEEP"
    FINANCE_BROAD = "FINANCE_BROAD"
    DUAL = "DUAL"


class ContentMode(str, Enum):
    FORMAL_ARTICLE = "FORMAL_ARTICLE"


class DeliveryChannel(str, Enum):
    WORD_FILE_ONLY = "WORD_FILE_ONLY"


class ArtifactKind(str, Enum):
    FINANCE_DEEP_DOCX = "FINANCE_DEEP_DOCX"
    FINANCE_BROAD_DOCX = "FINANCE_BROAD_DOCX"
    AUDIT_DOCX = "AUDIT_DOCX"


class TaskContract(BaseModel):
    """Immutable Financial business/output contract, intentionally identity-free.

    Article identity belongs to the Financial article state/workspace aggregate. Keeping
    identity out of this value object prevents a second task-id namespace inside the
    domain and keeps routing/output choices separate from lifecycle identity.
    """

    prompt: str
    source_refs: list[str] = Field(default_factory=list)
    target_platforms: list[str] = Field(default_factory=list)
    distribution_mode: DistributionMode = DistributionMode.DUAL
    content_mode: ContentMode = ContentMode.FORMAL_ARTICLE
    delivery_channel: DeliveryChannel = DeliveryChannel.WORD_FILE_ONLY
    required_outputs: list[ArtifactKind] = Field(default_factory=list)
    run_constraints: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def enforce_required_outputs(self):
        required = [ArtifactKind.AUDIT_DOCX]
        if self.distribution_mode in (DistributionMode.FINANCE_DEEP, DistributionMode.DUAL):
            required.append(ArtifactKind.FINANCE_DEEP_DOCX)
        if self.distribution_mode in (DistributionMode.FINANCE_BROAD, DistributionMode.DUAL):
            required.append(ArtifactKind.FINANCE_BROAD_DOCX)

        if not self.required_outputs:
            self.required_outputs = required
            return self

        if self.required_outputs != required:
            raise ValueError(
                "required_outputs must exactly match the canonical output set for "
                f"distribution_mode={self.distribution_mode.value}: "
                f"expected={[kind.value for kind in required]}, "
                f"actual={[kind.value for kind in self.required_outputs]}"
            )
        return self
