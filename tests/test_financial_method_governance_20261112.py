"""Existing Financial method-catalog governance; no new business state ledger."""
import json
from pathlib import Path
from copy import deepcopy
import hashlib
import time

import pytest

from financial_writing_agent.method_governance import (
    MethodGovernanceError, _digest, mutate_method_catalog, query_methods,
    validate_method_catalog,
)
from financial_writing_agent.provider_attestation import payload_sha256, request_sha256
from financial_writing_agent.whole_system_assurance import audit_repository_business_changes
from financial_writing_agent.standalone_runtime import (
    FinancialAdmissionError, FinancialEffectUnverified, _blob_sha,
    admit_method_action, observe_method_catalog,
)
from trusted_provider_testkit import (
    signed_attestation, signed_action_effect, signed_method_action_authorization,
    signed_method_impact, signed_method_promotion,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = "knowledge/METHOD_KNOWLEDGE_CATALOG.json"
METHOD_ID = "METHOD-SYNTHETIC-EVIDENCE-GOVERNANCE"


def original():
    return json.loads((ROOT / CATALOG_PATH).read_text(encoding="utf-8"))


def method():
    return {
        "knowledge_id": METHOD_ID,
        "category": "financial_research_method",
        "method": "Require an evidence list and material counterexample before selecting a company thesis.",
        "source_refs": ["method-source://primary"],
        "fit": "Material A-share economics research with company comparisons.",
        "misfit": "Trivial formatting does not need material causal research.",
        "adoption": "CANDIDATE_NOT_PROMOTED",
        "revalidation_trigger": "New contradiction or better research mechanism.",
    }


def decision():
    d = json.loads((ROOT / "evals/FINANCIAL_WRITING_KERNEL_DECISION_ENVELOPE_2026-10-15.json").read_text())
    d["evidence"].append({
        "ref": "method-source://primary", "kind": "EXTERNAL_METHOD",
        "summary": "Method source was compared with other approaches", "source_family": "method-original",
    })
    return d


def mutate(cat, operation, *, proposed=None, method_id=METHOD_ID,
           promotion_evidence=None, promotion_verifier=None,
           impact_target_revision=None, impact_evidence=None, impact_verifier=None,
           decision_envelope=None, evidence_refs=None, affected_stages=None):
    params = {
        "knowledge_id": method_id,
        "decision_envelope": decision_envelope or decision(),
        "evidence_refs": list(evidence_refs or ["method-source://primary"]),
        "affected_stages": list(affected_stages or ["RESEARCH", "EDITORIAL"]),
    }
    if proposed is not None:
        params["proposed_record"] = proposed
    if promotion_evidence is not None:
        params["promotion_evidence"] = promotion_evidence
    if impact_target_revision is not None:
        params["impact_target_revision"] = impact_target_revision
    if impact_evidence is not None:
        params["impact_evidence"] = impact_evidence
    raw = json.dumps(cat, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    action_request = {
        "schema_version": "1.0", "domain_id": "financial_writing",
        "action_id": f"synthetic-method-{operation.lower()}-{cat.get('governance_revision', 0) + 1}",
        "operation": operation, "expected_catalog_blob_sha": _blob_sha(raw),
        "parameters": params,
    }
    return mutate_method_catalog(
        cat, operation=operation, knowledge_id=method_id,
        proposed_record=proposed, decision_envelope=params["decision_envelope"],
        evidence_refs=params["evidence_refs"], affected_stages=params["affected_stages"],
        promotion_evidence=promotion_evidence, promotion_verifier=promotion_verifier,
        impact_target_revision=impact_target_revision, impact_evidence=impact_evidence,
        impact_verifier=impact_verifier, action_request=action_request,
        authorization_evidence=signed_method_action_authorization(action_request),
        observed_catalog_blob_sha=_blob_sha(raw),
    )


def test_old_catalog_is_queryable_without_reclassifying_legacy_as_verified():
    cat = validate_method_catalog(original())
    r = query_methods(cat, knowledge_id="METHOD-WSJ-NUT-GRAF")
    assert len(r) == 1
    assert r[0]["lifecycle_status"] == "LEGACY_DECLARED"
    assert r[0]["knowledge_id"] == "METHOD-WSJ-NUT-GRAF"


def test_create_method_stays_candidate_and_cannot_be_silently_activated():
    old = original()
    cat, receipt = mutate(old, "CREATE", proposed=method())
    assert old != cat
    assert receipt["operation"] == "CREATE"
    assert query_methods(cat, knowledge_id=METHOD_ID)[0]["lifecycle_status"] == "CANDIDATE"
    assert query_methods(cat, operational_only=True) == []
    assert cat["governance_revision"] == 1
    assert len(cat["change_history"]) == 1
    assert cat["change_history"][-1]["impact_review_state"] == "OPEN__AFFECTED_WORKFLOWS_REVALIDATION_REQUIRED"


def test_revision_of_legacy_or_active_method_is_staged_not_silent_overwrite():
    cat = original()
    old_record = query_methods(cat, knowledge_id="METHOD-WSJ-NUT-GRAF")[0]
    proposed = deepcopy({k: v for k, v in old_record.items() if k not in {
        "lifecycle_status", "pending_revision", "method_revision",
    }})
    proposed["method"] = "An entirely revised nut-graf strategy subject to downstream evaluation."
    revised, _ = mutate(cat, "REVISE", method_id="METHOD-WSJ-NUT-GRAF", proposed=proposed)
    after = query_methods(revised, knowledge_id="METHOD-WSJ-NUT-GRAF")[0]
    assert after["method"] == old_record["method"]
    assert after["pending_revision"]["method"] == proposed["method"]
    assert after["lifecycle_status"] == "LEGACY_DECLARED"
    assert revised["change_history"][-1]["operation"] == "REVISE"


def test_unreviewed_method_promotion_is_fail_closed_even_with_self_attested_pass_labels():
    cat, _ = mutate(original(), "CREATE", proposed=method())
    before = deepcopy(cat)
    evidence = {"validation_refs": ["ci://somebody-said-PASS"], "review_ref": "review://fake"}
    with pytest.raises(MethodGovernanceError, match="INDEPENDENT"):
        mutate(cat, "PROMOTE", promotion_evidence=evidence)
    assert cat == before


def promotion_verifier(request):
    return signed_method_promotion(request)


def test_verified_promotion_then_challenge_then_retire_is_append_only():
    cat, _ = mutate(original(), "CREATE", proposed=method())
    evidence = {"validation_refs": ["synthetic-ci://exact-change-test"], "review_ref": "simulation://review"}
    promoted, _ = mutate(cat, "PROMOTE", promotion_evidence=evidence,
                         promotion_verifier=promotion_verifier)
    assert query_methods(promoted, operational_only=True)[0]["knowledge_id"] == METHOD_ID
    challenged, _ = mutate(promoted, "CHALLENGE")
    assert query_methods(challenged, operational_only=True) == []
    retired, _ = mutate(challenged, "RETIRE")
    assert len(retired["records"]) == len(original()["records"]) + 1
    assert query_methods(retired, knowledge_id=METHOD_ID)[0]["lifecycle_status"] == "RETIRED"
    assert query_methods(retired, operational_only=True) == []
    assert [x["operation"] for x in retired["change_history"]] == [
        "CREATE", "PROMOTE", "CHALLENGE", "RETIRE",
    ]
    assert original()["records"] == cat["records"][:len(original()["records"])]


def test_missing_competing_decision_and_impact_scope_cannot_change_method():
    with pytest.raises(MethodGovernanceError):
        mutate(
            original(), "CREATE", proposed=method(),
            decision_envelope={"decision_id": "guess"},
            evidence_refs=["self://idea"], affected_stages=[],
        )


class Provider:
    def __init__(self):
        self.store = {CATALOG_PATH: json.dumps(original(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
        self.tamper = False

    def read(self, path):
        raw = self.store.get(path)
        if raw is None:
            return None
        return {"content": raw, "state": json.loads(raw), "blob_sha": _blob_sha(raw)}

    def read_effect(self, path):
        raw = self.store.get(path)
        return None if raw is None else {"content": raw, "blob_sha": _blob_sha(raw)}

    def write(self, path, previous, content):
        raw = self.store.get(path)
        if raw is None or _blob_sha(raw) != previous:
            raise RuntimeError("stale CAS")
        if not self.tamper:
            self.store[path] = content
        return {"blob_sha": _blob_sha(content), "commit_ref": "simulation://catalog"}

    def write_bundle(self, path, previous, files):
        raw = self.store.get(path)
        if raw is None or _blob_sha(raw) != previous:
            raise RuntimeError("stale bundle CAS")
        for ref in files:
            if ref != path and ref in self.store:
                raise RuntimeError("effect receipt already exists")
        if not self.tamper:
            self.store.update(files)
        return {
            "blob_shas": {ref: _blob_sha(content) for ref, content in files.items()},
            "commit_ref": "simulation://catalog-bundle",
        }

    def request(self, operation, *, expected=None, proposed=None,
                promotion_evidence=None, impact_target_revision=None,
                impact_evidence=None):
        parameters = {
            "knowledge_id": METHOD_ID,
            "proposed_record": proposed,
            "decision_envelope": decision(),
            "evidence_refs": ["method-source://primary"],
            "affected_stages": ["RESEARCH", "EDITORIAL"],
        }
        if promotion_evidence is not None:
            parameters["promotion_evidence"] = promotion_evidence
        if impact_target_revision is not None:
            parameters["impact_target_revision"] = impact_target_revision
        if impact_evidence is not None:
            parameters["impact_evidence"] = impact_evidence
        return {
            "schema_version": "1.0", "domain_id": "financial_writing",
            "action_id": "synthetic-method-" + operation.lower(),
            "operation": operation,
            "expected_catalog_blob_sha": expected or self.read(CATALOG_PATH)["blob_sha"],
            "parameters": parameters,
        }


def test_financial_method_cas_port_reads_real_catalog_and_never_writes_caos_or_article():
    p = Provider()
    before = p.read(CATALOG_PATH)["blob_sha"]
    r = admit_method_action(p.request("CREATE", proposed=method()),
                            catalog_reader=p.read, catalog_cas_writer=p.write,
                            authorization_verifier=signed_method_action_authorization,
                            catalog_bundle_cas_writer=p.write_bundle,
                            effect_attestation_signer=signed_action_effect,
                            effect_receipt_reader=p.read_effect)
    observed = observe_method_catalog(
        catalog_reader=p.read, effect_receipt_reader=p.read_effect,
    )
    assert r["method_catalog_cas_verified"] is True
    assert r["method_effect_receipt_readback_verified"] is True
    assert r["previous_catalog_blob_sha"] == before
    assert observed["effect_history"]["verified_effect_receipts"] == 1
    assert len(observed["records"]) == len(original()["records"]) + 1
    assert set(p.store) == {CATALOG_PATH, r["effect_receipt_ref"]}


def test_financial_method_mutation_denies_stale_sha_auth_and_unverified_readback():
    p = Provider()
    before = deepcopy(p.store)
    with pytest.raises(FinancialAdmissionError, match="AUTHORIZATION"):
        admit_method_action(p.request("CREATE", proposed=method()),
                            catalog_reader=p.read, catalog_cas_writer=p.write,
                            authorization_verifier=lambda _: False,
                            catalog_bundle_cas_writer=p.write_bundle,
                            effect_attestation_signer=signed_action_effect,
                            effect_receipt_reader=p.read_effect)
    assert p.store == before
    with pytest.raises(FinancialAdmissionError, match="CHANGED_CONCURRENTLY"):
        admit_method_action(p.request("CREATE", expected="f"*40, proposed=method()),
                            catalog_reader=p.read, catalog_cas_writer=p.write,
                            authorization_verifier=signed_method_action_authorization,
                            catalog_bundle_cas_writer=p.write_bundle,
                            effect_attestation_signer=signed_action_effect,
                            effect_receipt_reader=p.read_effect)
    assert p.store == before
    p.tamper = True
    with pytest.raises(FinancialEffectUnverified):
        admit_method_action(p.request("CREATE", proposed=method()),
                            catalog_reader=p.read, catalog_cas_writer=p.write,
                            authorization_verifier=signed_method_action_authorization,
                            catalog_bundle_cas_writer=p.write_bundle,
                            effect_attestation_signer=signed_action_effect,
                            effect_receipt_reader=p.read_effect)
    assert p.store == before


def test_method_revalidation_obligation_cannot_be_silently_closed_by_self_pass():
    cat, _ = mutate(original(), "CREATE", proposed=method())
    target = cat["change_history"][-1]
    assert target["impact_review_state"].startswith("OPEN")
    before = deepcopy(cat)
    with pytest.raises(MethodGovernanceError, match="IMPACT"):
        mutate(
            cat, "VERIFY_IMPACT", impact_target_revision=1,
            impact_evidence={
                "stage_evidence_refs": {
                    "RESEARCH": "simulation://source-and-company-research-test",
                    "EDITORIAL": "simulation://story-selection-test",
                },
            },
        )
    assert cat == before


def test_method_impact_closure_requires_exact_original_event_and_stage_evidence():
    cat, _ = mutate(original(), "CREATE", proposed=method())
    challenge_seen = []

    def trusted_impact_verifier(request):
        challenge_seen.append(request)
        return signed_method_impact(request)

    closed, receipt = mutate(
        cat, "VERIFY_IMPACT", impact_target_revision=1,
        impact_evidence={
            "stage_evidence_refs": {
                "RESEARCH": "simulation://source-and-company-research-test",
                "EDITORIAL": "simulation://story-selection-test",
            },
        },
        impact_verifier=trusted_impact_verifier,
    )
    assert challenge_seen
    assert closed["change_history"][0]["impact_review_state"].startswith("OPEN")
    assert closed["change_history"][-1]["operation"] == "VERIFY_IMPACT"
    assert closed["change_history"][-1]["target_change_revision"] == 1
    assert receipt["impact_review_state"].startswith("CLOSED")
    assert query_methods(closed, knowledge_id=METHOD_ID)[0]["lifecycle_status"] == "CANDIDATE"
    p = Provider()
    p.store[CATALOG_PATH] = json.dumps(closed, ensure_ascii=False)
    observed = observe_method_catalog(catalog_reader=p.read)
    assert observed["open_revalidation"] == []
    assert observed["live_article_effect_verified"] is False


def test_method_impact_stamps_effective_version_and_ignores_pending_unpromoted_revisions():
    from financial_writing_agent.method_governance import (
        admitted_method_usage_snapshot, method_dependency_drift,
    )

    catalog, _ = mutate(original(), "CREATE", proposed=method())
    catalog, _ = mutate(catalog, "PROMOTE", promotion_evidence={
        "validation_refs": ["synthetic-ci://exact-change-test"], "review_ref": "simulation://review",
    }, promotion_verifier=promotion_verifier)
    snapshot = admitted_method_usage_snapshot(catalog, [METHOD_ID])
    assert snapshot["methods"][0]["knowledge_id"] == METHOD_ID
    assert method_dependency_drift(catalog, snapshot) == []
    tentative = method()
    tentative["method"] = "A new research method that is not yet effective."
    pending, _ = mutate(catalog, "REVISE", proposed=tentative)
    assert method_dependency_drift(pending, snapshot) == []
    promoted, _ = mutate(pending, "PROMOTE", promotion_evidence={
        "validation_refs": ["synthetic-ci://exact-change-test"], "review_ref": "simulation://review",
    }, promotion_verifier=promotion_verifier)
    delta = method_dependency_drift(promoted, snapshot)
    assert len(delta) == 1
    assert delta[0]["knowledge_id"] == METHOD_ID
    assert delta[0]["earliest_affected_stage"] == "RESEARCH"
    assert delta[0]["current_lifecycle_status"] == "ACTIVE"
    assert delta[0]["change_revisions"] == [4]


def test_historical_method_action_promotion_and_impact_receipts_remain_readable_after_freshness_window():
    cat, _ = mutate(original(), "CREATE", proposed=method())
    cat, _ = mutate(
        cat, "PROMOTE",
        promotion_evidence={
            "validation_refs": ["synthetic-ci://exact-change-test"],
            "review_ref": "simulation://review",
        },
        promotion_verifier=promotion_verifier,
    )
    cat, _ = mutate(
        cat, "VERIFY_IMPACT", impact_target_revision=1,
        impact_evidence={"stage_evidence_refs": {
            "RESEARCH": "simulation://research",
            "EDITORIAL": "simulation://editorial",
        }},
        impact_verifier=lambda request: signed_method_impact(request),
    )
    old_issued_at = int(time.time()) - 86400
    for event in cat["change_history"]:
        request = event["authorization_request"]
        event["authorization_evidence"] = signed_attestation(
            "method_action_authorization", issued_at=old_issued_at,
            approved=True, action_id=request["action_id"],
            domain_id=request["domain_id"], operation=request["operation"],
            knowledge_id=request["parameters"]["knowledge_id"],
            expected_catalog_blob_sha=request["expected_catalog_blob_sha"],
            request_sha256=request_sha256(request),
        )
        promoted = event.get("promoted_proof")
        if promoted is not None:
            promoted["attestation"] = signed_attestation(
                "method_promotion_review", actor="synthetic-method-reviewer",
                key_env="FINANCIAL_METHOD_REVIEW_KEY",
                provider_env="FINANCIAL_METHOD_REVIEW_PROVIDER_ID",
                issued_at=old_issued_at, approved=True,
                knowledge_id=event["knowledge_id"],
                record_sha256=promoted["reviewed_record_sha256"],
                decision_sha256=event["decision_sha256"],
                validation_refs=promoted["validation_refs"],
                review_ref=promoted["review_ref"],
            )
            promoted["attestation_signature"] = promoted["attestation"]["signature"]
        impact = event.get("impact_verification")
        if impact is not None:
            target = cat["change_history"][impact["target_change_revision"] - 1]
            impact["reviewed_event_sha256"] = _digest(target)
            impact["attestation"] = signed_attestation(
                "method_impact_review", actor="synthetic-method-reviewer",
                key_env="FINANCIAL_METHOD_REVIEW_KEY",
                provider_env="FINANCIAL_METHOD_REVIEW_PROVIDER_ID",
                issued_at=old_issued_at, approved=True,
                knowledge_id=event["knowledge_id"],
                target_change_revision=impact["target_change_revision"],
                event_sha256=impact["reviewed_event_sha256"],
                stage_evidence_refs=impact["stage_evidence_refs"],
                verified_stages=impact["verified_stages"],
            )
            impact["attestation_signature"] = impact["attestation"]["signature"]
    checked = validate_method_catalog(cat)
    assert query_methods(checked, operational_only=True)[0]["knowledge_id"] == METHOD_ID


def test_method_retirement_invalidates_prior_article_method_snapshot():
    from financial_writing_agent.method_governance import (
        admitted_method_usage_snapshot, method_dependency_drift,
    )

    catalog, _ = mutate(original(), "CREATE", proposed=method())
    catalog, _ = mutate(catalog, "PROMOTE", promotion_evidence={
        "validation_refs": ["synthetic-ci://exact-change-test"], "review_ref": "simulation://review",
    }, promotion_verifier=promotion_verifier)
    snapshot = admitted_method_usage_snapshot(catalog, [METHOD_ID])
    retired, _ = mutate(catalog, "RETIRE")
    change = method_dependency_drift(retired, snapshot)
    assert change[0]["current_lifecycle_status"] == "RETIRED"
    assert change[0]["change_revisions"] == [3]

def test_method_effect_receipt_is_required_and_binds_exact_catalog_blob():
    p = Provider()
    result = admit_method_action(
        p.request("CREATE", proposed=method()),
        catalog_reader=p.read, catalog_cas_writer=p.write,
        authorization_verifier=signed_method_action_authorization,
        catalog_bundle_cas_writer=p.write_bundle,
        effect_attestation_signer=signed_action_effect,
        effect_receipt_reader=p.read_effect,
    )
    effect_ref = result["effect_receipt_ref"]
    saved = p.store.pop(effect_ref)
    with pytest.raises(FinancialAdmissionError, match="METHOD_EFFECT_RECEIPT_MISSING"):
        observe_method_catalog(catalog_reader=p.read, effect_receipt_reader=p.read_effect)
    p.store[effect_ref] = saved

    effect = json.loads(saved)
    effect["resulting_catalog_blob_sha"] = "0" * 40
    p.store[effect_ref] = json.dumps(effect, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    with pytest.raises(FinancialAdmissionError, match="PERSISTED_EFFECT_ATTESTATION_INVALID"):
        observe_method_catalog(catalog_reader=p.read, effect_receipt_reader=p.read_effect)


def test_method_catalog_cannot_roll_back_to_unbound_event_after_effect_bound_history():
    p = Provider()
    admit_method_action(
        p.request("CREATE", proposed=method()),
        catalog_reader=p.read, catalog_cas_writer=p.write,
        authorization_verifier=signed_method_action_authorization,
        catalog_bundle_cas_writer=p.write_bundle,
        effect_attestation_signer=signed_action_effect,
        effect_receipt_reader=p.read_effect,
    )
    bound = p.read(CATALOG_PATH)["state"]
    legacy, _ = mutate(bound, "CHALLENGE")
    p.store[CATALOG_PATH] = json.dumps(legacy, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    with pytest.raises(FinancialAdmissionError, match="EFFECT_BOUND_HISTORY_ROLLBACK"):
        observe_method_catalog(catalog_reader=p.read, effect_receipt_reader=p.read_effect)


def test_method_catalog_pr_audit_requires_atomic_effect_receipt_and_replays_exact_operation():
    p = Provider()
    old_raw = p.store[CATALOG_PATH].encode("utf-8")
    result = admit_method_action(
        p.request("CREATE", proposed=method()),
        catalog_reader=p.read, catalog_cas_writer=p.write,
        authorization_verifier=signed_method_action_authorization,
        catalog_bundle_cas_writer=p.write_bundle,
        effect_attestation_signer=signed_action_effect,
        effect_receipt_reader=p.read_effect,
    )
    new_raw = p.store[CATALOG_PATH].encode("utf-8")
    effect_ref = result["effect_receipt_ref"]
    files = {ref: value.encode("utf-8") for ref, value in p.store.items()}
    accepted = audit_repository_business_changes(
        [CATALOG_PATH, effect_ref],
        before_reader=lambda ref: old_raw if ref == CATALOG_PATH else None,
        after_reader=lambda ref: files.get(ref),
    )
    assert accepted["violations"] == []
    assert accepted["status"] == "NO_UNADMITTED_BUSINESS_CHANGE_OBSERVED"

    missing = audit_repository_business_changes(
        [CATALOG_PATH, effect_ref],
        before_reader=lambda ref: old_raw if ref == CATALOG_PATH else None,
        after_reader=lambda ref: new_raw if ref == CATALOG_PATH else None,
    )
    assert missing["status"].startswith("REJECTED")
    assert any("METHOD_EFFECT_RECEIPT" in issue for issue in missing["violations"])


def test_method_catalog_pr_audit_rejects_validly_signed_but_unreplayed_lifecycle_transition():
    p = Provider()
    admit_method_action(
        p.request("CREATE", proposed=method()),
        catalog_reader=p.read, catalog_cas_writer=p.write,
        authorization_verifier=signed_method_action_authorization,
        catalog_bundle_cas_writer=p.write_bundle,
        effect_attestation_signer=signed_action_effect,
        effect_receipt_reader=p.read_effect,
    )
    admit_method_action(
        p.request("PROMOTE", promotion_evidence={
            "validation_refs": ["synthetic-ci://exact-change-test"],
            "review_ref": "simulation://review",
        }),
        catalog_reader=p.read, catalog_cas_writer=p.write,
        authorization_verifier=signed_method_action_authorization,
        catalog_bundle_cas_writer=p.write_bundle,
        effect_attestation_signer=signed_action_effect,
        effect_receipt_reader=p.read_effect,
        promotion_verifier=promotion_verifier,
    )
    old_raw = p.store[CATALOG_PATH].encode("utf-8")
    challenge_result = admit_method_action(
        p.request("CHALLENGE"),
        catalog_reader=p.read, catalog_cas_writer=p.write,
        authorization_verifier=signed_method_action_authorization,
        catalog_bundle_cas_writer=p.write_bundle,
        effect_attestation_signer=signed_action_effect,
        effect_receipt_reader=p.read_effect,
    )
    catalog = p.read(CATALOG_PATH)["state"]
    assert catalog["records"][-1]["lifecycle_status"] == "CHALLENGED"
    catalog["records"][-1]["lifecycle_status"] = "RETIRED"
    catalog["change_history"][-1]["result_record_sha256"] = _digest(catalog["records"][-1])
    new_raw = (json.dumps(catalog, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    request = catalog["change_history"][-1]["authorization_request"]
    authorization = catalog["change_history"][-1]["authorization_evidence"]
    effect_ref = challenge_result["effect_receipt_ref"]
    effect_claims = {
        "approved": True,
        "action_id": request["action_id"],
        "domain_id": "financial_writing",
        "catalog_ref": CATALOG_PATH,
        "operation": request["operation"],
        "knowledge_id": request["parameters"]["knowledge_id"],
        "previous_catalog_blob_sha": request["expected_catalog_blob_sha"],
        "resulting_catalog_blob_sha": _blob_sha(new_raw),
        "request_sha256": request_sha256(request),
        "authorization_sha256": payload_sha256(authorization),
        "effect_contract_version": "1.0",
        "admission_runtime": "financial_writing_agent.standalone_runtime.admit_method_action",
    }
    p.store[CATALOG_PATH] = new_raw.decode("utf-8")
    p.store[effect_ref] = json.dumps(
        signed_action_effect(effect_claims), ensure_ascii=False, sort_keys=True, indent=2,
    ) + "\n"
    files = {ref: value.encode("utf-8") for ref, value in p.store.items()}
    rejected = audit_repository_business_changes(
        [CATALOG_PATH, effect_ref],
        before_reader=lambda ref: old_raw if ref == CATALOG_PATH else None,
        after_reader=lambda ref: files.get(ref),
    )
    assert rejected["status"].startswith("REJECTED")
    assert any("ACTION_REPLAY_RESULT_DIFFERS" in issue for issue in rejected["violations"])

