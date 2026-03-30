"""Parse human-entered page lists like ``1,3-5,8`` into 1-based page numbers."""


def parse_page_list(spec: str) -> list[int]:
    """
    Turn a spec like ``1, 3-5, 8`` into a flat list of positive integers in order.

    Ranges are inclusive; if start > end, the range is still expanded low-to-high
    (so ``5-3`` becomes 3,4,5).
    """
    s = spec.strip().replace(" ", "")
    if not s:
        raise ValueError("Page list is empty.")

    out: list[int] = []
    for part in s.split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
            if start > end:
                start, end = end, start
            if start < 1:
                raise ValueError("Page numbers must be at least 1.")
            out.extend(range(start, end + 1))
        else:
            n = int(part)
            if n < 1:
                raise ValueError("Page numbers must be at least 1.")
            out.append(n)

    if not out:
        raise ValueError("No pages parsed.")
    return out
