from __future__ import annotations

import json
from importlib.resources import files

_PACKAGE = "financial_writing_agent"


def read_reference(name: str) -> str:
    resource = files(_PACKAGE).joinpath("resources", "references", name)
    return resource.read_text(encoding="utf-8")


def load_packaged_policy() -> dict:
    resource = files(_PACKAGE).joinpath("resources", "policy.json")
    return json.loads(resource.read_text(encoding="utf-8"))
