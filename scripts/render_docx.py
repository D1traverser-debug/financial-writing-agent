from __future__ import annotations

import argparse

from financial_writing_agent.rendering import render_docx_pages


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    print("\n".join(render_docx_pages(args.docx, args.out)))


if __name__ == "__main__":
    main()
