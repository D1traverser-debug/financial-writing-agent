"""Canonical identity boundaries for Financial article-owned artifacts.

This is a shared invariant, not a new controller or business state authority.
All paths are Git repository POSIX paths, not host filesystem paths.
"""
from __future__ import annotations

import re
from typing import Any

_TASK_SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


def require_task_id(value: Any) -> str:
    if not isinstance(value, str) or not _TASK_SLUG.fullmatch(value):
        raise ValueError("task_id must be a canonical one-segment ASCII article slug")
    return value


def require_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        raise ValueError("path must be a nonempty relative POSIX path")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("path contains empty, current, or parent path segment")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("path contains control characters")
    if ":" in value or value.startswith("~"):
        raise ValueError("path contains ambiguous path syntax")
    return value


def require_article_path(value: Any, task_id: Any) -> str:
    slug = require_task_id(task_id)
    path = require_relative_path(value)
    prefix = f"workspaces/articles/{slug}/"
    if not path.startswith(prefix) or not path[len(prefix):]:
        raise ValueError("path is not inside the exact article workspace")
    return path


def require_basename(value: Any) -> str:
    path = require_relative_path(value)
    if "/" in path or path in (".", ".."):
        raise ValueError("file name must be a canonical basename")
    return path


def require_word_basename(value: Any) -> str:
    """Enforce the actual Word-only filename contract at every delivery boundary."""
    name = require_basename(value)
    if not name.lower().endswith(".docx") or not name[:-5].strip():
        raise ValueError("Word delivery file name must have a nonempty .docx stem")
    return name
