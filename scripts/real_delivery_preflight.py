"""Fail-closed mechanical preflight for actual, task-scoped Word portfolio files.

This CLI reuses Financial's canonical Word checker; it is not a second owner
runtime, provider signature, semantic review, or permission grant.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from docx import Document

from financial_writing_agent.checks import check_docx
from financial_writing_agent.resources import load_packaged_policy

ALLOWED_KINDS = frozenset({
    "FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX",
    "PLATFORM_INTERACTION_PACK_DOCX", "AUDIT_DOCX", "PRIVATE_RESEARCH_DOCX",
})
ARTICLE_KINDS = frozenset({"FINANCE_DEEP_DOCX", "FINANCE_BROAD_DOCX"})


def preflight(manifest: dict[str, Any], *, manifest_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    items: dict[str, dict[str, Any]] = {}
    required = manifest.get("required_outputs")
    artifacts = manifest.get("artifacts")
    evidence = manifest.get("article_evidence")
    if not isinstance(required, list) or not required or len(required) != len(set(map(str, required))):
        errors.append("REQUIRED_OUTPUTS_MISSING_OR_DUPLICATE")
        required = []
    if not set(required).issubset(ALLOWED_KINDS):
        errors.append("UNSUPPORTED_OUTPUT_KIND")
    if not isinstance(artifacts, dict):
        errors.append("ARTIFACT_MAP_REQUIRED")
        artifacts = {}
    if set(artifacts) != set(required):
        errors.append("REQUIRED_ARTIFACT_SET_MISMATCH")
    if not isinstance(evidence, dict):
        evidence = {}
    policy = load_packaged_policy()
    for kind in required:
        if kind not in ALLOWED_KINDS:
            continue
        item_errors: list[str] = []
        ref = artifacts.get(kind)
        if not isinstance(ref, str) or not ref.strip():
            item_errors.append("FILE_PATH_REQUIRED")
            path = None
        else:
            path = Path(ref)
            if not path.is_absolute():
                path = manifest_dir / path
            if path.suffix.lower() != ".docx" or not path.is_file():
                item_errors.append("DOCX_FILE_MISSING")
                path = None
        if path is not None:
            try:
                doc = Document(path)
                if not any(p.text.strip() for p in doc.paragraphs) and not doc.tables:
                    item_errors.append("EMPTY_DOCUMENT")
                if kind == "PLATFORM_INTERACTION_PACK_DOCX" and doc.tables:
                    item_errors.append("INTERACTION_TABLE_FORBIDDEN")
                if kind in ARTICLE_KINDS:
                    metadata = evidence.get(kind)
                    if not isinstance(metadata, dict):
                        item_errors.append("ARTICLE_EVIDENCE_METADATA_REQUIRED")
                    else:
                        names = metadata.get("stock_names")
                        anchors = metadata.get("required_bold_anchors")
                        if not isinstance(names, list) or not all(isinstance(x, str) for x in names):
                            item_errors.append("STOCK_NAME_INPUT_REQUIRED")
                        if (not isinstance(anchors, list) or not anchors
                                or not all(isinstance(x, str) and x.strip() for x in anchors)):
                            item_errors.append("SEMANTIC_ANCHOR_INPUT_REQUIRED")
                        if isinstance(names, list) and isinstance(anchors, list) and anchors:
                            check = check_docx(
                                path, stock_names=names, policy=policy,
                                required_bold_anchors=anchors,
                                require_risk_disclaimer=True,
                                require_deep_navigation=(kind == "FINANCE_DEEP_DOCX"),
                            )
                            item_errors.extend(check["errors"])
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
            except Exception as exc:
                item_errors.append("DOCX_UNREADABLE:" + type(exc).__name__)
                digest = None
        else:
            digest = None
        items[kind] = {
            "file": str(path) if path is not None else str(ref or ""),
            "sha256": digest,
            "mechanical_status": "FAIL" if item_errors else "PASS",
            "errors": item_errors,
        }
        errors.extend(f"{kind}:{error}" for error in item_errors)
    return {
        "schema_version": "1.0",
        "task_id": manifest.get("task_id"),
        "mechanical_status": "FAIL" if errors else "PASS",
        "items": items,
        "errors": errors,
        "assurance": "SESSION_FILE_MECHANICAL_CHECK_ONLY",
        "publication_certification": "OPEN",
        "independent_reader_acceptance": "OPEN",
        "financial_fact_entailment": "NOT_VERIFIED_BY_THIS_GATE",
        "company_universe_completeness": "NOT_VERIFIED_BY_THIS_GATE",
        "owner_state_admission": "NOT_VERIFIED_BY_THIS_GATE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args(argv)
    try:
        obj = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("manifest must be a JSON object")
        result = preflight(obj, manifest_dir=args.manifest.resolve().parent)
    except (OSError, ValueError, TypeError) as exc:
        result = {
            "schema_version": "1.0", "mechanical_status": "FAIL",
            "errors": ["MANIFEST_INVALID:" + type(exc).__name__],
            "publication_certification": "OPEN",
        }
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if result["mechanical_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
