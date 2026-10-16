from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any, Mapping
from urllib import error, parse, request

DEFAULT_REPOSITORY = "D1traverser-debug/financial-writing-agent"
DEFAULT_REF = "main"
DEFAULT_TIMEOUT_SECONDS = 10.0


class AuthoritativeStateError(ValueError):
    pass


def _json_type_strict_equal(left: Any, right: Any) -> bool:
    """Compare JSON-shaped values without Python's bool/int equality collapse."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        if left.keys() != right.keys():
            return False
        return all(_json_type_strict_equal(left[key], right[key]) for key in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _json_type_strict_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    return left == right


class TypeStrictJsonDict(dict[str, Any]):
    """Root JSON object whose equality preserves JSON scalar/container types."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mapping):
            return False
        return _json_type_strict_equal(dict(self), dict(other))

    def __ne__(self, other: object) -> bool:
        return not self == other


@dataclass(frozen=True)
class AuthoritativeStateSnapshot:
    task_id: str
    state: dict[str, Any]
    blob_sha: str
    path: str
    ref: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "state", TypeStrictJsonDict(self.state))


def _canonical_task_id(task_id: Any) -> str:
    if not isinstance(task_id, str) or not task_id:
        raise AuthoritativeStateError("task_id is required for authoritative GitHub state resolution")
    if task_id != task_id.strip():
        raise AuthoritativeStateError("task_id must not contain leading or trailing whitespace")
    return task_id


def _state_path(task_id: str) -> str:
    return f"workspaces/articles/{task_id}/STATE.json"


def _github_contents_url(repository: str, path: str, ref: str) -> str:
    encoded_path = parse.quote(path, safe="/")
    encoded_ref = parse.quote(ref, safe="")
    return f"https://api.github.com/repos/{repository}/contents/{encoded_path}?ref={encoded_ref}"


def _github_blob_url(repository: str, blob_sha: str) -> str:
    return f"https://api.github.com/repos/{repository}/git/blobs/{blob_sha}"


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "financial-writing-agent-authoritative-state",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _read_json(url: str, *, headers: Mapping[str, str], timeout: float, label: str) -> Mapping[str, Any]:
    req = request.Request(url, headers=dict(headers))
    try:
        with request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise AuthoritativeStateError(f"{label}: HTTP {exc.code}") from exc
    except (error.URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthoritativeStateError(f"{label}: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise AuthoritativeStateError(f"{label}: GitHub response must be an object")
    return payload


def _decode_base64_json(encoded: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(encoded, str):
        raise AuthoritativeStateError(f"{label}: base64 content is missing")
    try:
        raw = base64.b64decode(encoded, validate=False)
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthoritativeStateError(f"{label}: authoritative GitHub STATE.json could not be decoded") from exc
    if not isinstance(parsed, dict):
        raise AuthoritativeStateError(f"{label}: authoritative GitHub STATE.json must contain a JSON object")
    return parsed


def fetch_authoritative_state(
    task_id: str,
    *,
    repository: str = DEFAULT_REPOSITORY,
    ref: str = DEFAULT_REF,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> AuthoritativeStateSnapshot:
    """Read the authoritative persisted Financial state directly from GitHub.

    The Contents API establishes path/type and the authoritative Git blob SHA. For
    small files it also supplies inline base64 content. Once GitHub stops inlining
    content (notably for files larger than 1 MB), the resolver follows the validated
    SHA through the Git Blob API and requires that response to return the same SHA.
    This preserves one authority identity across both size regimes.
    """
    clean_task_id = _canonical_task_id(task_id)
    if repository != DEFAULT_REPOSITORY:
        raise AuthoritativeStateError("authoritative Financial state repository is fixed by domain ownership")
    if ref != DEFAULT_REF:
        raise AuthoritativeStateError("authoritative Financial business state must resolve from main")

    path = _state_path(clean_task_id)
    headers = _headers()
    contents_label = f"authoritative GitHub state read failed for {path}"
    payload = _read_json(
        _github_contents_url(repository, path, ref),
        headers=headers,
        timeout=timeout,
        label=contents_label,
    )

    if payload.get("type") != "file":
        raise AuthoritativeStateError("authoritative GitHub state path must resolve to a file")
    if payload.get("path") != path:
        raise AuthoritativeStateError("authoritative GitHub state path mismatch")

    blob_sha = str(payload.get("sha", "")).strip().lower()
    if len(blob_sha) != 40 or any(ch not in "0123456789abcdef" for ch in blob_sha):
        raise AuthoritativeStateError("authoritative GitHub state response lacks a valid blob SHA")

    if payload.get("encoding") == "base64" and isinstance(payload.get("content"), str):
        parsed = _decode_base64_json(payload.get("content"), label=contents_label)
    else:
        blob_label = f"authoritative GitHub blob read failed for {path}@{blob_sha}"
        blob_payload = _read_json(
            _github_blob_url(repository, blob_sha),
            headers=headers,
            timeout=timeout,
            label=blob_label,
        )
        returned_sha = str(blob_payload.get("sha", "")).strip().lower()
        if returned_sha != blob_sha:
            raise AuthoritativeStateError("authoritative GitHub blob SHA mismatch")
        if blob_payload.get("encoding") != "base64":
            raise AuthoritativeStateError("authoritative GitHub blob response must provide base64 content")
        parsed = _decode_base64_json(blob_payload.get("content"), label=blob_label)

    if parsed.get("task_id") != clean_task_id:
        raise AuthoritativeStateError("authoritative GitHub STATE.json task_id mismatch")

    return AuthoritativeStateSnapshot(
        task_id=clean_task_id,
        state=parsed,
        blob_sha=blob_sha,
        path=path,
        ref=ref,
    )
