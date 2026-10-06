from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ownership = json.loads((ROOT / "config" / "rule_ownership.json").read_text(encoding="utf-8"))
    reverse = {}
    dup = []
    for owner, keys in ownership.items():
        for key in keys:
            if key in reverse:
                dup.append((key, reverse[key], owner))
            reverse[key] = owner
    if dup:
        raise SystemExit(f"duplicate rule ownership: {dup}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    packaged = (ROOT / "skills" / "financial-writing-agent" / "SKILL.md").read_text(encoding="utf-8")
    for token in [
        "references/research.md",
        "references/knowledge.md",
        "references/editorial.md",
        "references/style.md",
        "references/visuals.md",
        "references/delivery.md",
        "references/audit.md",
    ]:
        if token not in skill:
            raise SystemExit(f"SKILL missing reference: {token}")
    authority = "MCP runtime checkpoint is the executable authority"
    if authority not in skill or authority not in packaged:
        raise SystemExit("root/packaged SKILL recovery authority is not aligned")
    if "unspecified platform" not in packaged or "DUAL" not in packaged:
        raise SystemExit("packaged SKILL missing unspecified-platform DUAL default")
    print(f"PASS: {len(reverse)} owned rule groups; no duplicate owner keys; root/packaged recovery authority aligned")


if __name__ == "__main__":
    main()
