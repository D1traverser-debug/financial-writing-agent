import json
from pathlib import Path


def test_unique_rule_ownership():
    data = json.loads(Path("config/rule_ownership.json").read_text(encoding="utf-8"))
    seen = set()
    for _, keys in data.items():
        for key in keys:
            assert key not in seen, key
            seen.add(key)


def test_writing_core_has_no_image_workflow_terms():
    core = "\n".join(
        Path(p).read_text(encoding="utf-8")
        for p in ["SKILL.md", "references/research.md", "references/editorial.md", "references/delivery.md", "references/audit.md"]
    ).lower()
    for token in ["封面图", "段落图", "配图", "image generation", "生成图片"]:
        assert token not in core
