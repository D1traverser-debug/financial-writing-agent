from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def render_docx_pages(docx_path: str | Path, out_dir: str | Path) -> list[str]:
    docx = Path(docx_path).resolve()
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    soffice = shutil.which("libreoffice") or shutil.which("soffice")
    pdftoppm = shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        raise RuntimeError("libreoffice/soffice and pdftoppm are required for render QA")
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out), str(docx)],
        check=True,
        capture_output=True,
        text=True,
    )
    pdf = out / f"{docx.stem}.pdf"
    if not pdf.exists():
        raise RuntimeError("PDF render was not created")
    subprocess.run(
        [pdftoppm, "-png", "-r", "110", str(pdf), str(out / "page")],
        check=True,
        capture_output=True,
        text=True,
    )
    pages = sorted(out.glob("page-*.png"))
    if not pages:
        raise RuntimeError("No page PNGs produced")
    return [str(page) for page in pages]
