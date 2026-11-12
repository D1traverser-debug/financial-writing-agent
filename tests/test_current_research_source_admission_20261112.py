"""Current research source admitter must not accept stale or fictitious citations."""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from financial_writing_agent.current_research_sources import (
    CurrentResearchEvidenceError,
    verify_current_research_sources,
)
from financial_writing_agent.private_research import REQUIRED_MODULES

ROOT = Path(__file__).resolve().parents[1]


def _brief(as_of):
    return {
        "contract_version": "1.1", "as_of": as_of,
        "coverage_state": "COMPLETE", "unresolved_gaps": [],
        "modules": {
            name: {"status": "APPLICABLE", "summary": f"synthetic module {i}",
                   "evidence_refs": [f"source://{i}"]}
            for i, name in enumerate(REQUIRED_MODULES)
        },
    }


def _source(ref, now):
    i = int(ref.split("/")[-1])
    text = f"这是用于复核来源读取的真实字节回调测试数据片段 {i}，不是任何财经真实性认可。"
    return {
        "text": text, "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "retrieved_at": now.isoformat(),
        "source_family": "ISSUER_FILINGS" if i % 2 else "GOVERNMENT_RECORD",
    }


def test_all_modules_are_read_and_digests_bound_without_publishing_raw_content():
    now = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)
    proof = verify_current_research_sources(
        _brief(now.isoformat()),
        source_reader=lambda ref: _source(ref, now),
        as_of=now,
    )
    assert proof["source_snapshots_observed"] == len(REQUIRED_MODULES) == 15
    assert proof["source_families"] == ["GOVERNMENT_RECORD", "ISSUER_FILINGS"]
    assert proof["financial_facts_verified"] is False
    assert "用于复核来源读取" not in json.dumps(proof, ensure_ascii=False)


def test_real_old_cross_border_private_brief_is_not_admissible_as_current_without_refresh():
    raw = json.loads((ROOT / "workspaces/articles/cross-border-ecommerce-20261016-v2/research/PRIVATE_RESEARCH_BRIEF_1_1_20261016.json").read_text(encoding="utf-8"))
    now = datetime(2026, 11, 12, tzinfo=timezone.utc)
    with pytest.raises(CurrentResearchEvidenceError, match="BRIEF_STALE"):
        verify_current_research_sources(raw, source_reader=lambda _: None, as_of=now)


def test_fake_or_unread_source_ref_blocks_even_if_modules_marked_complete():
    now = datetime(2026, 11, 12, tzinfo=timezone.utc)
    with pytest.raises(CurrentResearchEvidenceError, match="SOURCE_NOT_FOUND"):
        verify_current_research_sources(
            _brief(now.isoformat()), source_reader=lambda _: None, as_of=now,
        )


def test_digest_forgery_and_single_source_family_fail_closed():
    now = datetime(2026, 11, 12, tzinfo=timezone.utc)
    def forged(ref):
        row = _source(ref, now)
        row["sha256"] = "f" * 64
        return row
    with pytest.raises(CurrentResearchEvidenceError, match="SHA_MISMATCH"):
        verify_current_research_sources(_brief(now.isoformat()), source_reader=forged, as_of=now)

    def one_family(ref):
        row = _source(ref, now)
        row["source_family"] = "SAME_ONLY"
        return row
    with pytest.raises(CurrentResearchEvidenceError, match="TWO_SOURCE_FAMILIES_REQUIRED"):
        verify_current_research_sources(_brief(now.isoformat()), source_reader=one_family, as_of=now)


def test_provider_snapshot_stale_does_not_get_falsely_refreshed_by_a_new_brief():
    now = datetime(2026, 11, 12, tzinfo=timezone.utc)
    def stale(ref):
        row = _source(ref, now)
        row["retrieved_at"] = (now - timedelta(days=40)).isoformat()
        return row
    with pytest.raises(CurrentResearchEvidenceError, match="SNAPSHOT_STALE"):
        verify_current_research_sources(_brief(now.isoformat()), source_reader=stale, as_of=now)
