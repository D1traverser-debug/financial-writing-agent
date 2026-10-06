from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    docx = Path(args.docx).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    soffice = shutil.which("libreoffice") or shutil.which("soffice")
    pdftoppm = shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        raise SystemExit("libreoffice/soffice and pdftoppm are required for render QA")
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out), str(docx)], check=True)
    pdf = out / f"{docx.stem}.pdf"
    if not pdf.exists():
        raise SystemExit("PDF render was not created")
    subprocess.run([pdftoppm, "-png", "-r", "110", str(pdf), str(out / "page")], check=True)
    pages = sorted(out.glob("page-*.png"))
    if not pages:
        raise SystemExit("No page PNGs produced")
    print("\n".join(str(p) for p in pages))


if __name__ == "__main__":
    main()
