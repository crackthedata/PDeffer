"""Resolve paths strictly under a data root (for Docker-mounted host folders)."""

from __future__ import annotations

from pathlib import Path


def data_root() -> Path:
    import os

    env = os.environ.get("PDEFFER_DATA")
    if env:
        return Path(env).resolve()
    # Local dev: use ./pdfs under the current working directory (Dockerfile sets PDEFFER_DATA=/data)
    return (Path.cwd() / "pdfs").resolve()


def resolve_under_root(root: Path, relative: str) -> Path:
    """
    Return ``root / relative`` if the result stays under ``root``.

    ``relative`` must be a relative path without ``..`` (single file or subfolder).
    """
    rel = Path(relative)
    if rel.is_absolute():
        raise ValueError("Path must be relative.")
    parts = rel.parts
    if ".." in parts:
        raise ValueError("Invalid path.")

    candidate = (root / rel).resolve()
    root_r = root.resolve()
    try:
        candidate.relative_to(root_r)
    except ValueError:
        raise ValueError("Path escapes data directory.") from None
    return candidate


def list_pdfs(root: Path) -> list[str]:
    """Basenames of ``*.pdf`` directly under ``root`` (not recursive)."""
    root = root.resolve()
    if not root.is_dir():
        return []
    names: list[str] = []
    for p in sorted(root.iterdir()):
        if p.is_file() and p.suffix.lower() == ".pdf":
            names.append(p.name)
    return names


def list_docs(root: Path) -> list[str]:
    """Basenames of Word documents (``*.docx`` / ``*.doc``) directly under ``root``."""
    root = root.resolve()
    if not root.is_dir():
        return []
    names: list[str] = []
    for p in sorted(root.iterdir()):
        if not p.is_file():
            continue
        suf = p.suffix.lower()
        if suf in {".docx", ".doc"}:
            names.append(p.name)
    return names
