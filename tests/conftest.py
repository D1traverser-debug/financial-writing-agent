from __future__ import annotations

import pytest

from financial_writing_agent import owner_guard


@pytest.fixture(autouse=True)
def _unit_authority_stub(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    """Keep ordinary unit tests deterministic without weakening production APIs.

    Production owner mutations resolve the current STATE.json from GitHub. Most unit
    tests exercise workflow semantics with synthetic in-memory states and dummy blob
    SHAs, so they replace only the private authority-resolution boundary. Tests marked
    ``strict_authority`` keep the production boundary and provide an explicit fake
    GitHub snapshot instead.
    """
    if request.node.get_closest_marker("strict_authority") is not None:
        return

    def _stub(state, *, expected_blob_sha=None):
        return None

    monkeypatch.setattr(owner_guard, "_resolve_authoritative_state", _stub)
