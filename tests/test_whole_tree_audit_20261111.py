"""The whole-repository machine audit must observe every currently tracked file.

This is byte/parse verification, not an independent semantic review of each
line; source coverage is measured separately by coverage.py.
"""
import subprocess

from scripts.whole_tree_audit import ROOT, scan_tree


def test_all_tracked_financial_files_scanned_and_hashed_without_missing_bytes():
    scanned = scan_tree()
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    names = [x.decode("utf-8") for x in tracked.split(b"\x00") if x]
    results = scanned["files"]
    assert scanned["scope"] == "ALL_GIT_TRACKED_FILES__BYTE_PARSE_AUDIT_ONLY"
    assert scanned["semantic_line_by_line_review_completed"] is False
    assert scanned["editorial_product_certified"] is False
    assert scanned["all_current_writes_mediated"] is False
    assert len(results) == len(names) and len(results) > 250
    assert {x["path"] for x in results} == set(names)
    assert len({x["sha256"] for x in results}) > 200
    assert all(len(item["sha256"]) == 64 for item in results)
    assert scanned["python_ast_parsed"] >= 75
    assert scanned["json_parsed_unique_keys"] >= 45
    assert scanned["current_workspace_manifest_count"] == 1
    assert scanned["errors"] == []


def test_active_modules_and_all_current_text_have_nonempty_machine_inspection():
    scanned = scan_tree()
    files = {x["path"]: x for x in scanned["files"]}
    for name in (
        "financial_writing_agent/owner_guard.py",
        "financial_writing_agent/current_admission.py",
        "financial_writing_agent/standalone_runtime.py",
        "financial_writing_agent/task_publication.py",
        "financial_writing_agent/delivery_pipeline.py",
        "financial_writing_agent/writing_kernel.py",
    ):
        assert files[name]["inspection_level"] == "PYTHON_AST_PARSED__NO_SEMANTIC_OR_TEST_CLAIM"
        assert files[name]["line_count"] > 0
    assert files["docs/product_requirements.md"]["inspection_level"] == "ALL_TEXT_BYTES_UTF8_DECODED"
