from __future__ import annotations

from .models import ArtifactKind

# Owner-state required_outputs remains the historically stable business contract.
# This presentation contract governs what this user's Financial system must actually
# expose in a current chat after the owner artifacts are reconciled.
REQUIRED_SUPPLEMENTAL_VISIBLE_OUTPUTS: tuple[ArtifactKind, ...] = (
    ArtifactKind.PRIVATE_RESEARCH_DOCX,
)

# Durable user-owned Word presentation constraints. Delivery normalizes these before
# construction and verifies their absence afterward, so compliance does not depend on
# the drafting model remembering a formatting preference.
FORBIDDEN_VISIBLE_CHARACTERS: tuple[str, ...] = ("·",)
TEXT_SUBSTITUTIONS: dict[str, str] = {"·": "、"}

CANONICAL_DELIVERY_PATH = "financial_writing_agent.delivery_pipeline"
