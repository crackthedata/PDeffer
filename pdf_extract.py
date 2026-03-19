"""Extract selected pages from a PDF into a new file."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def extract_pages(
    input_path: str | Path,
    output_path: str | Path,
    page_numbers: list[int],
) -> None:
    """
    Write a new PDF containing only the given pages from ``input_path``.

    ``page_numbers`` uses 1-based indexing (first page is 1), in the order
    you list them; duplicates are allowed and repeat that page in the output.
    """
    src = Path(input_path)
    dst = Path(output_path)
    if not page_numbers:
        raise ValueError("page_numbers must not be empty")

    reader = PdfReader(str(src))
    n = len(reader.pages)
    writer = PdfWriter()

    for p in page_numbers:
        if p < 1 or p > n:
            raise ValueError(f"Page {p} is out of range for {src.name} (valid: 1–{n})")
        writer.add_page(reader.pages[p - 1])

    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "wb") as f:
        writer.write(f)
