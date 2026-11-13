from pathlib import Path

import pytest

from financial_writing_agent import rendering


def test_render_requires_both_external_binaries(tmp_path, monkeypatch):
    monkeypatch.setattr(rendering.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="libreoffice/soffice and pdftoppm"):
        rendering.render_docx_pages(tmp_path / "article.docx", tmp_path / "render")


def test_render_removes_stale_products_and_returns_only_fresh_pages(tmp_path, monkeypatch):
    docx = tmp_path / "article.docx"
    docx.write_bytes(b"synthetic docx path")
    out = tmp_path / "render"
    out.mkdir()
    (out / "article.pdf").write_bytes(b"stale pdf")
    (out / "page-1.png").write_bytes(b"stale page")
    (out / "page-2.png").write_bytes(b"stale page")

    def which(name):
        return {"libreoffice": "/usr/bin/libreoffice", "pdftoppm": "/usr/bin/pdftoppm"}.get(name)

    def run(command, **kwargs):
        if command[0].endswith("libreoffice"):
            output_dir = Path(command[command.index("--outdir") + 1])
            (output_dir / "article.pdf").write_bytes(b"fresh pdf")
        else:
            prefix = Path(command[-1])
            (prefix.parent / "page-1.png").write_bytes(b"fresh page 1")
            (prefix.parent / "page-2.png").write_bytes(b"fresh page 2")

    monkeypatch.setattr(rendering.shutil, "which", which)
    monkeypatch.setattr(rendering.subprocess, "run", run)

    pages = rendering.render_docx_pages(docx, out)

    assert pages == [str(out / "page-1.png"), str(out / "page-2.png")]
    assert (out / "article.pdf").read_bytes() == b"fresh pdf"
    assert (out / "page-1.png").read_bytes() == b"fresh page 1"
    assert (out / "page-2.png").read_bytes() == b"fresh page 2"


def test_render_fails_if_office_does_not_create_pdf(tmp_path, monkeypatch):
    docx = tmp_path / "article.docx"
    docx.write_bytes(b"synthetic docx path")
    monkeypatch.setattr(rendering.shutil, "which", lambda name: "/usr/bin/tool")
    monkeypatch.setattr(rendering.subprocess, "run", lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError, match="PDF render was not created"):
        rendering.render_docx_pages(docx, tmp_path / "render")


def test_render_fails_if_pdf_has_no_png_pages(tmp_path, monkeypatch):
    docx = tmp_path / "article.docx"
    docx.write_bytes(b"synthetic docx path")
    monkeypatch.setattr(rendering.shutil, "which", lambda name: "/usr/bin/tool")

    def run(command, **kwargs):
        if "--convert-to" in command:
            out_dir = Path(command[command.index("--outdir") + 1])
            (out_dir / "article.pdf").write_bytes(b"fresh pdf")

    monkeypatch.setattr(rendering.subprocess, "run", run)
    with pytest.raises(RuntimeError, match="No page PNGs produced"):
        rendering.render_docx_pages(docx, tmp_path / "render")
