"""Flask UI for self-hosted Docker; reads/writes PDFs under PDEFFER_DATA only."""

from __future__ import annotations

import os
import re
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, url_for

from page_spec import parse_page_list
from paths_safe import data_root, list_pdfs, resolve_under_root
from pdf_extract import extract_pages
from pdf_merge import merge_pdfs

app = Flask(__name__)
app.secret_key = os.environ.get("PDEFFER_SECRET_KEY", "dev-change-in-production")


def _safe_output_name(name: str) -> str:
    name = name.strip()
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    base = Path(name).name
    if not base or base != name or ".." in base or "/" in base or "\\" in base:
        raise ValueError("Output must be a simple filename (e.g. out.pdf).")
    return base


@app.route("/")
def index():
    root = data_root()
    root.mkdir(parents=True, exist_ok=True)
    files = list_pdfs(root)
    return render_template("index.html", files=files, data_dir=str(root))


@app.post("/extract")
def extract():
    root = data_root()
    try:
        src_name = request.form.get("source", "").strip()
        pages_raw = request.form.get("pages", "").strip()
        out_name = request.form.get("output", "").strip()
        if not src_name or not pages_raw or not out_name:
            flash("Source, pages, and output name are required.", "error")
            return redirect(url_for("index"))

        src = resolve_under_root(root, src_name)
        if not src.is_file():
            flash("Source file not found.", "error")
            return redirect(url_for("index"))

        pages = parse_page_list(pages_raw)
        out = resolve_under_root(root, _safe_output_name(out_name))
        extract_pages(src, out, pages)
        flash(f"Saved {out.name}", "ok")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("index"))


def _parse_merge_order(text: str) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("Add at least one filename (one per line).")
    for ln in lines:
        if "/" in ln or "\\" in ln or ".." in ln:
            raise ValueError(f"Invalid filename: {ln}")
    return lines


@app.post("/merge")
def merge():
    root = data_root()
    try:
        order_text = request.form.get("merge_files", "")
        out_name = request.form.get("merge_output", "").strip()
        if not out_name:
            flash("Merge output filename is required.", "error")
            return redirect(url_for("index"))

        names = _parse_merge_order(order_text)
        paths: list[Path] = []
        for n in names:
            p = resolve_under_root(root, n)
            if not p.is_file():
                raise ValueError(f"Missing PDF: {n}")
            paths.append(p)

        out = resolve_under_root(root, _safe_output_name(out_name))
        merge_pdfs(paths, out)
        flash(f"Merged to {out.name}", "ok")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("index"))


@app.post("/upload")
def upload():
    root = data_root()
    root.mkdir(parents=True, exist_ok=True)
    f = request.files.get("file")
    if not f or not f.filename:
        flash("No file selected.", "error")
        return redirect(url_for("index"))
    raw = Path(f.filename).name
    if not raw.lower().endswith(".pdf"):
        flash("Only .pdf uploads are allowed.", "error")
        return redirect(url_for("index"))
    if not re.match(r"^[\w.\- ()\[\]]+\.pdf$", raw, re.I):
        flash("Filename has unsupported characters.", "error")
        return redirect(url_for("index"))
    try:
        dest = resolve_under_root(root, raw)
        f.save(str(dest))
        flash(f"Uploaded {raw}", "ok")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("index"))


@app.get("/download/<path:name>")
def download(name: str):
    root = data_root()
    try:
        path = resolve_under_root(root, name)
    except ValueError:
        flash("Invalid file.", "error")
        return redirect(url_for("index"))
    if not path.is_file():
        flash("File not found.", "error")
        return redirect(url_for("index"))
    return send_file(path, as_attachment=True, download_name=path.name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
