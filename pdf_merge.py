"""Combine multiple PDFs in order into one file."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def merge_pdfs(input_paths: list[str | Path], output_path: str | Path) -> None:
    """
    Concatenate PDFs in ``input_paths`` order into ``output_path``.

    Each file is appended in full; pages from earlier paths appear first.
    """
    if not input_paths:
        raise ValueError("input_paths must not be empty")

    writer = PdfWriter()
    for path in input_paths:
        p = Path(path)
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        writer.write(f)
