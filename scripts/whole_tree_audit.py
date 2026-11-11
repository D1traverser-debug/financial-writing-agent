"""Enumerate and mechanically inspect every tracked Financial repository text file.

This is a complete-byte inventory and parse audit, NOT a claim that every
sentence was independently understood or that article quality is verified.
Coverage data is produced separately by real pytest execution and remains
distinct from this inventory.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".json", ".md", ".csv", ".yml", ".yaml", ".toml", ".txt"}
CURRENT_STATE_NAME = "STATE.json"
CURRENT_MANIFEST_NAME = "ARTIFACT_STATUS.json"


def _git_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True,
    )
    names = [x.decode("utf-8") for x in proc.stdout.split(b"\x00") if x]
    if len(names) != len(set(names)):
        raise ValueError("GIT_TRACKED_FILE_LIST_HAS_DUPLICATES")
    return sorted(names)


def _no_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for name, value in pairs:
        if name in mapped:
            raise ValueError(f"DUPLICATE_JSON_KEY:{name}")
        mapped[name] = value
    return mapped


def _kind(path: str) -> str:
    if path.startswith("financial_writing_agent/") and path.endswith(".py"):
        return "ACTIVE_PYTHON"
    if path.startswith("tests/") and path.endswith(".py"):
        return "PYTHON_TEST"
    if path.startswith("scripts/") and path.endswith(".py"):
        return "TOOLING_PYTHON"
    if path.startswith("workspaces/articles/"):
        return "ARTICLE_WORKSPACE_OR_HISTORY"
    if path.startswith("evals/"):
        return "EVALUATION_AND_HISTORY"
    if path.startswith("references/") or "/references/" in path:
        return "REFERENCE_MIRROR"
    if path.endswith(".json"):
        return "CONTRACT_OR_DATA"
    return "OTHER_TRACKED_TEXT"


def scan_tree() -> dict[str, Any]:
    names = _git_files()
    if not names:
        raise ValueError("EMPTY_TRACKED_TREE")
    report: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    parsed_py = 0
    parsed_json = 0
    current_manifest_paths: list[Path] = []
    for name in names:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            errors.append(f"INVALID_TRACKED_FILE:{name}")
            continue
        raw = path.read_bytes()
        entry: dict[str, Any] = {
            "path": name, "kind": _kind(name), "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "inspection_level": "BYTES_READ_ONLY",
        }
        if path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith(".gitignore"):
            try:
                decoded = raw.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"TRACKED_TEXT_NOT_UTF8:{name}")
                report.append(entry)
                continue
            entry["line_count"] = len(decoded.splitlines())
            entry["inspection_level"] = "ALL_TEXT_BYTES_UTF8_DECODED"
            if path.suffix == ".py":
                try:
                    tree = ast.parse(decoded, filename=name)
                except SyntaxError as exc:
                    errors.append(f"PYTHON_AST_FAILED:{name}:{exc.lineno}:{exc.msg}")
                else:
                    parsed_py += 1
                    entry["inspection_level"] = "PYTHON_AST_PARSED__NO_SEMANTIC_OR_TEST_CLAIM"
                    entry["top_level_definitions"] = [
                        node.name for node in tree.body
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    ]
            elif path.suffix == ".json":
                try:
                    parsed = json.loads(decoded, object_pairs_hook=_no_duplicate_json_keys)
                except (ValueError, json.JSONDecodeError) as exc:
                    # Historical snapshots are immutable provenance. List issues but
                    # do not 'repair' old bytes or silently certify them as current.
                    item = f"JSON_PARSE_OR_DUPLICATE_FAILED:{name}:{str(exc)[:200]}"
                    if name.startswith("workspaces/articles/") or name.startswith("evals/"):
                        warnings.append(item)
                    else:
                        errors.append(item)
                else:
                    parsed_json += 1
                    entry["inspection_level"] = "JSON_PARSED_AND_UNIQUE_KEYS__NO_SEMANTIC_CLAIM"
                    if path.name == CURRENT_MANIFEST_NAME and isinstance(parsed, dict):
                        if parsed.get("workspace_lifecycle") == "CURRENT":
                            current_manifest_paths.append(path)
        report.append(entry)

    for manifest_path in current_manifest_paths:
        try:
            from financial_writing_agent.artifact_hygiene import validate_artifact_status_manifest
            from financial_writing_agent.current_admission import validate_state
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"),
                                  object_pairs_hook=_no_duplicate_json_keys)
            validate_artifact_status_manifest(manifest)
            declared = manifest["current_authority"]
            state_path = ROOT / declared
            if not state_path.is_file():
                raise ValueError("CURRENT_AUTHORITY_STATE_NOT_FOUND")
            state = json.loads(state_path.read_text(encoding="utf-8"),
                               object_pairs_hook=_no_duplicate_json_keys)
            validate_state(state)
            if state.get("task_id") != manifest.get("task_id"):
                raise ValueError("CURRENT_STATE_TASK_ID_MISMATCH")
        except Exception as exc:
            errors.append(f"CURRENT_WORKSPACE_OWNER_AUDIT_FAILED:{manifest_path.relative_to(ROOT)}:{exc}")

    total_lines = sum(item.get("line_count", 0) for item in report)
    return {
        "schema_version": "1.0",
        "scope": "ALL_GIT_TRACKED_FILES__BYTE_PARSE_AUDIT_ONLY",
        "semantic_line_by_line_review_completed": False,
        "editorial_product_certified": False,
        "all_current_writes_mediated": False,
        "git_tracked_file_count": len(names),
        "bytes_total": sum(item["size_bytes"] for item in report),
        "text_line_count": total_lines,
        "python_ast_parsed": parsed_py,
        "json_parsed_unique_keys": parsed_json,
        "current_workspace_manifest_count": len(current_manifest_paths),
        "files": report,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("audit/whole_tree.json"))
    args = parser.parse_args()
    scan = scan_tree()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(scan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(
        f"Whole Financial tree byte/parse audit: {scan['git_tracked_file_count']} tracked, "
        f"{scan['python_ast_parsed']} Python AST, "
        f"{scan['json_parsed_unique_keys']} JSON parsed, "
        f"{scan['text_line_count']} decoded text lines, "
        f"warnings={len(scan['warnings'])}, errors={len(scan['errors'])}; "
        f"semantic review and article-readiness NOT claimed"
    )
    for item in scan["warnings"][:20]:
        print("WARN:", item)
    for item in scan["errors"]:
        print("FAIL:", item)
    if scan["errors"]:
        raise SystemExit("whole-tree machine audit found active defects")


if __name__ == "__main__":
    main()
