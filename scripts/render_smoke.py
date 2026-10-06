from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        docx_path = tmp / "render_smoke.docx"
        outdir = tmp / "rendered"
        doc = Document()
        doc.add_heading("Financial Writing Agent Render Smoke", level=1)
        doc.add_paragraph("Render validation must produce at least one PNG page.")
        doc.save(docx_path)
        proc = subprocess.run(
            [sys.executable, str(root / "scripts" / "render_docx.py"), str(docx_path), "--out", str(outdir)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise SystemExit(proc.stderr.strip() or proc.stdout.strip() or "render smoke failed")
        pages = [Path(line.strip()) for line in proc.stdout.splitlines() if line.strip().endswith(".png")]
        if not pages or not all(p.exists() and p.stat().st_size > 0 for p in pages):
            raise SystemExit("render smoke did not produce valid PNG pages")
        print(f"PASS: DOCX render pipeline produced {len(pages)} PNG page(s)")


if __name__ == "__main__":
    main()
