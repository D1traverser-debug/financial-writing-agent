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
from financial_writing_agent.private_research import REQUIRED_MODULES, V1_0_REQUIRED_MODULES
from financial_writing_agent.standalone_runtime import _verify_delivery_research_freshness

ROOT = Path(__file__).resolve().parents[1]


def _brief(as_of, version="1.1"):
    modules = REQUIRED_MODULES if version == "1.1" else V1_0_REQUIRED_MODULES
    return {
        "contract_version": version, "as_of": as_of,
        "coverage_state": "COMPLETE", "unresolved_gaps": [],
        "modules": {
            name: {"status": "APPLICABLE", "summary": f"synthetic module {i}",
                   "evidence_refs": [f"source://{i}"]}
            for i, name in enumerate(modules)
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



def test_legacy_1_0_private_research_uses_its_original_module_set_for_source_readback():
    now = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)
    brief = _brief(now.isoformat(), version="1.0")
    proof = verify_current_research_sources(
        brief,
        source_reader=lambda ref: _source(ref, now),
        as_of=now,
    )
    assert proof["private_research_contract_version"] == "1.0"
    assert proof["source_snapshots_observed"] == len(V1_0_REQUIRED_MODULES) == 12


def _package_source(ref, now, family):
    text = f"用于全股票池证据链集成测试的来源正文，引用标识为 {ref}，仅验证读取绑定。"
    return {
        "text": text,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "retrieved_at": now.isoformat(),
        "source_family": family,
    }


def _research_package_sources():
    return {
        "evidence_ledger": [
            {"source": "source://eastmoney"},
            {"source": "source://tonghuashun"},
            {"source": "source://company-filing"},
        ],
        "universe_coverage": {
            "recall_sources": ["source://eastmoney", "source://tonghuashun"],
            "recall_source_families": ["EASTMONEY", "TONGHUASHUN"],
        },
    }


def _brief_with_package_sources(now):
    brief = _brief(now.isoformat())
    brief["modules"][REQUIRED_MODULES[0]]["evidence_refs"].extend([
        "source://eastmoney",
        "source://tonghuashun",
        "source://company-filing",
    ])
    return brief


def test_full_universe_company_evidence_sources_are_read_back_via_private_brief_binding():
    now = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)
    brief = _brief_with_package_sources(now)
    package = _research_package_sources()

    def reader(ref):
        families = {
            "source://eastmoney": "EASTMONEY",
            "source://tonghuashun": "TONGHUASHUN",
            "source://company-filing": "ISSUER_FILINGS",
        }
        if ref in families:
            return _package_source(ref, now, families[ref])
        return _source(ref, now)

    proof = verify_current_research_sources(
        brief, source_reader=reader, research_package=package, as_of=now,
    )
    assert proof["source_snapshots_observed"] == len(REQUIRED_MODULES) + 3
    assert proof["universe_recall_source_families"] == ["eastmoney", "tonghuashun"]


def test_full_universe_package_company_evidence_not_in_private_brief_is_rejected():
    now = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)
    brief = _brief(now.isoformat())
    with pytest.raises(
        CurrentResearchEvidenceError,
        match="PACKAGE_EVIDENCE_NOT_BOUND_TO_PRIVATE_BRIEF",
    ):
        verify_current_research_sources(
            brief,
            source_reader=lambda ref: _source(ref, now),
            research_package=_research_package_sources(),
            as_of=now,
        )


def test_full_universe_declared_recall_families_must_match_provider_readback():
    now = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)
    brief = _brief_with_package_sources(now)
    package = _research_package_sources()

    def reader(ref):
        families = {
            "source://eastmoney": "EASTMONEY",
            "source://tonghuashun": "EASTMONEY",
            "source://company-filing": "ISSUER_FILINGS",
        }
        if ref in families:
            return _package_source(ref, now, families[ref])
        return _source(ref, now)

    with pytest.raises(
        CurrentResearchEvidenceError,
        match="RECALL_SOURCE_FAMILY_MISMATCH",
    ):
        verify_current_research_sources(
            brief, source_reader=reader, research_package=package, as_of=now,
        )


def test_legacy_1_0_delivery_rechecks_source_freshness_instead_of_skipping():
    now = datetime.now(timezone.utc)
    brief = _brief(now.isoformat(), version="1.0")
    reader = lambda ref: _source(ref, now)
    readback = verify_current_research_sources(
        brief, source_reader=reader, as_of=now,
    )
    candidate = {
        "private_research_contract_version": "1.0",
        "quality_evidence": {"private_research_brief": brief},
        "execution_receipts": [{
            "stage": "RESEARCH",
            "input_bindings": {"research_source_readback": readback},
        }],
    }
    proof = _verify_delivery_research_freshness(candidate, reader)
    assert proof["source_set_unchanged"] is True
    assert proof["source_body_bytes_unchanged"] is True
