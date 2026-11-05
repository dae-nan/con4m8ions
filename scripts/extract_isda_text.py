#!/usr/bin/env python3
"""One-off: extract text from the ISDA/EMTA PDFs into docs/reference/isda/text/.

The workbook build reads only the committed .txt files, so it never needs a PDF tool.
Rerun this only when a PDF in docs/reference/isda/ changes. Requires poppler `pdftotext`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PDF_DIR = REPO / "docs/reference/isda"
TXT_DIR = PDF_DIR / "text"


def extract(pdf: Path) -> str:
    raw = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf), "-"], check=True, capture_output=True, text=True
    ).stdout
    pages = raw.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    return "".join(f"===== PAGE {i} =====\n{p.rstrip()}\n" for i, p in enumerate(pages, 1))


def main():
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        out = TXT_DIR / f"{pdf.stem}.txt"
        out.write_text(extract(pdf), encoding="utf-8")
        print("WROTE", out.relative_to(REPO))


if __name__ == "__main__":
    main()
