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


@dataclass(frozen=True)
class AuthoritativeStateSnapshot:
    task_id: str
    state: dict[str, Any]
    blob_sha: str
    path: str
    ref: str


def _state_path(task_id: str) -> str:
    return f"workspaces/articles/{task_id}/STATE.json"


def _github_contents_url(repository: str, path: str, ref: str) -> str:
    encoded_path = parse.quote(path, safe="/")
    encoded_ref = parse.quote(ref, safe="")
    return f"https://api.github.com/repos/{repository}/contents/{encoded_path}?ref={encoded_ref}"


def fetch_authoritative_state(
    task_id: str,
    *,
    repository: str = DEFAULT_REPOSITORY,
    ref: str = DEFAULT_REF,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> AuthoritativeStateSnapshot:
    """Read the authoritative persisted Financial state directly from GitHub.

    This resolver intentionally does not accept caller-supplied state content or a
    caller-supplied digest as authority. The GitHub contents response supplies both
    the persisted bytes and the immutable blob SHA used for mutation admission.
    Network/read failures fail closed.
    """
    clean_task_id = str(task_id).strip()
    if not clean_task_id:
        raise AuthoritativeStateError("task_id is required for authoritative GitHub state resolution")
    if repository != DEFAULT_REPOSITORY:
        raise AuthoritativeStateError("authoritative Financial state repository is fixed by domain ownership")
    if ref != DEFAULT_REF:
        raise AuthoritativeStateError("authoritative Financial business state must resolve from main")

    path = _state_path(clean_task_id)
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "financial-writing-agent-authoritative-state",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(_github_contents_url(repository, path, ref), headers=headers)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise AuthoritativeStateError(
            f"authoritative GitHub state read failed for {path}: HTTP {exc.code}"
        ) from exc
    except (error.URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthoritativeStateError(f"authoritative GitHub state read failed for {path}: {exc}") from exc

    if not isinstance(payload, Mapping):
        raise AuthoritativeStateError("GitHub state response must be an object")
    if payload.get("type") != "file":
        raise AuthoritativeStateError("authoritative GitHub state path must resolve to a file")
    if payload.get("path") != path:
        raise AuthoritativeStateError("authoritative GitHub state path mismatch")

    blob_sha = str(payload.get("sha", "")).strip()
    if len(blob_sha) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in blob_sha):
        raise AuthoritativeStateError("authoritative GitHub state response lacks a valid blob SHA")

    encoded = payload.get("content")
    encoding = payload.get("encoding")
    if encoding != "base64" or not isinstance(encoded, str):
        raise AuthoritativeStateError("authoritative GitHub state response must provide base64 file content")
    try:
        raw = base64.b64decode(encoded, validate=False)
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthoritativeStateError("authoritative GitHub STATE.json could not be decoded") from exc
    if not isinstance(parsed, dict):
        raise AuthoritativeStateError("authoritative GitHub STATE.json must contain a JSON object")
    if str(parsed.get("task_id", "")).strip() != clean_task_id:
        raise AuthoritativeStateError("authoritative GitHub STATE.json task_id mismatch")

    return AuthoritativeStateSnapshot(
        task_id=clean_task_id,
        state=parsed,
        blob_sha=blob_sha.lower(),
        path=path,
        ref=ref,
    )
