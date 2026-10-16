"""Test-only low-level owner fixture.

Production code must not use this helper. It exists only so owner_guard's legacy/base
state-machine invariants can still be unit-tested after current task creation is closed
to the public low-level builder.
"""

from financial_writing_agent import owner_guard


def build_legacy_owner_state(**kwargs):
    return owner_guard.build_initial_state(
        _current_admission_token=owner_guard._CURRENT_ADMISSION_TOKEN,
        **kwargs,
    )
