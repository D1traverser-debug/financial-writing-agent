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
    for token in ["references/research.md", "references/editorial.md", "references/delivery.md", "references/audit.md"]:
        if token not in skill:
            raise SystemExit(f"SKILL missing reference: {token}")
    print(f"PASS: {len(reverse)} owned rule groups; no duplicate owner keys")


if __name__ == "__main__":
    main()
