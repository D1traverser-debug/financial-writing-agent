from __future__ import annotations

from dataclasses import dataclass
import re


_H1 = re.compile(r"^##\s+(.+?)\s*$")
_H2 = re.compile(r"^###\s+(.+?)\s*$")


@dataclass(frozen=True)
class StructureGeometryResult:
    h1_count: int
    h2_counts: tuple[int, ...]
    max_same_child_count_run: int
    repeated_child_count: int | None
    mechanical_symmetry_alert: bool
    requires_revise: bool
    reason: str


def analyze_structure_geometry(markdown: str) -> StructureGeometryResult:
    """Detect extreme repeated H1→H2 geometry in publication markdown.

    Numbering itself is not an error. This check targets a narrower failure class:
    four or more consecutive substantive H1 sections all forced into the same three-or-more
    child count. That shape is strong deterministic evidence of repeated section geometry
    and must be revised before Natural Authorial Prose/template-redundancy can PASS.

    Short documents, H1-only Broad articles, and isolated parallel sections do not trigger.
    """
    if not isinstance(markdown, str):
        raise TypeError("markdown must be a string")

    counts: list[int] = []
    current: int | None = None
    for raw in markdown.splitlines():
        line = raw.strip()
        if _H1.match(line):
            if current is not None:
                counts.append(current)
            current = 0
        elif current is not None and _H2.match(line):
            current += 1
    if current is not None:
        counts.append(current)

    max_run = 0
    run_value: int | None = None
    run = 0
    repeated: int | None = None
    for value in counts:
        if value == run_value:
            run += 1
        else:
            run_value = value
            run = 1
        if run > max_run:
            max_run = run
            repeated = value

    alert = max_run >= 4 and repeated is not None and repeated >= 3
    reason = (
        f"{max_run} consecutive H1 sections each contain exactly {repeated} H2 children; "
        "this is extreme repeated section geometry"
        if alert
        else "no extreme repeated H1/H2 geometry detected"
    )
    return StructureGeometryResult(
        h1_count=len(counts),
        h2_counts=tuple(counts),
        max_same_child_count_run=max_run,
        repeated_child_count=repeated,
        mechanical_symmetry_alert=alert,
        requires_revise=alert,
        reason=reason,
    )
