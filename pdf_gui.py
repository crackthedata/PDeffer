"""extract pages from a PDF or merge PDFs in list order."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pdf_extract import extract_pages
from pdf_merge import merge_pdfs
from pypdf import PdfReader


def _page_count(path: str) -> int:
    reader = PdfReader(path)
    return len(reader.pages)


class PdfToolApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PDeffer — PDF extract & merge")
        self.minsize(520, 420)
        self.geometry("640x480")

        self._files: list[str] = []

        main = ttk.Frame(self, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="PDF files (order used for merge)").pack(anchor=tk.W)
        files_row = ttk.Frame(main)
        files_row.pack(fill=tk.BOTH, expand=True, pady=(4, 8))

        self._files_lb = tk.Listbox(files_row, selectmode=tk.SINGLE, exportselection=False)
        files_scroll = ttk.Scrollbar(files_row, orient=tk.VERTICAL, command=self._files_lb.yview)
        self._files_lb.configure(yscrollcommand=files_scroll.set)
        self._files_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        btn_col = ttk.Frame(files_row)
        btn_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        ttk.Button(btn_col, text="Add…", command=self._add_files).pack(fill=tk.X, pady=2)
        ttk.Button(btn_col, text="Remove", command=self._remove_selected_file).pack(fill=tk.X, pady=2)
        ttk.Button(btn_col, text="Up", command=lambda: self._move_file(-1)).pack(fill=tk.X, pady=2)
        ttk.Button(btn_col, text="Down", command=lambda: self._move_file(1)).pack(fill=tk.X, pady=2)

        self._files_lb.bind("<<ListboxSelect>>", self._on_file_pick)

        nb = ttk.Notebook(main)
        nb.pack(fill=tk.BOTH, expand=True)

        extract_tab = ttk.Frame(nb, padding=8)
        nb.add(extract_tab, text="Extract pages")

        ttk.Label(
            extract_tab,
            text="Select a PDF in the list above, then choose pages (Ctrl/Shift for multiple).",
        ).pack(anchor=tk.W)

        pages_row = ttk.Frame(extract_tab)
        pages_row.pack(fill=tk.BOTH, expand=True, pady=8)
        self._pages_lb = tk.Listbox(pages_row, selectmode=tk.EXTENDED, exportselection=False)
        ps = ttk.Scrollbar(pages_row, orient=tk.VERTICAL, command=self._pages_lb.yview)
        self._pages_lb.configure(yscrollcommand=ps.set)
        self._pages_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ps.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(extract_tab, text="Save selected pages as new PDF…", command=self._save_extract).pack(
            anchor=tk.W, pady=(4, 0)
        )

        merge_tab = ttk.Frame(nb, padding=8)
        nb.add(merge_tab, text="Merge PDFs")

        ttk.Label(
            merge_tab,
            text="Files are merged top-to-bottom in the order shown in the list.",
        ).pack(anchor=tk.W)
        ttk.Button(merge_tab, text="Merge all into one PDF…", command=self._save_merge).pack(
            anchor=tk.W, pady=12
        )

        self._status = tk.StringVar(value="Add one or more PDFs to begin.")
        ttk.Label(main, textvariable=self._status, foreground="#333").pack(anchor=tk.W, pady=(8, 0))

    def _add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Choose PDF files",
            filetypes=[("PDF", "*.pdf"), ("All files", "*.*")],
        )
        for p in paths:
            if p not in self._files:
                self._files.append(p)
                self._files_lb.insert(tk.END, p)
        if paths:
            self._status.set(f"{len(self._files)} file(s) in list.")

    def _remove_selected_file(self) -> None:
        sel = self._files_lb.curselection()
        if not sel:
            return
        i = sel[0]
        self._files_lb.delete(i)
        del self._files[i]
        self._pages_lb.delete(0, tk.END)
        self._status.set("Removed file.")

    def _move_file(self, delta: int) -> None:
        sel = self._files_lb.curselection()
        if not sel:
            return
        i = sel[0]
        j = i + delta
        if j < 0 or j >= len(self._files):
            return
        self._files[i], self._files[j] = self._files[j], self._files[i]
        label = self._files_lb.get(i)
        self._files_lb.delete(i)
        self._files_lb.insert(j, label)
        self._files_lb.selection_clear(0, tk.END)
        self._files_lb.selection_set(j)
        self._files_lb.see(j)
        if sel[0] == i:
            self._refresh_pages_for_index(j)

    def _on_file_pick(self, _evt=None) -> None:
        sel = self._files_lb.curselection()
        if not sel:
            return
        self._refresh_pages_for_index(sel[0])

    def _refresh_pages_for_index(self, index: int) -> None:
        self._pages_lb.delete(0, tk.END)
        if index < 0 or index >= len(self._files):
            return
        path = self._files[index]
        try:
            n = _page_count(path)
        except Exception as e:
            messagebox.showerror("PDF error", f"Could not read pages:\n{e}")
            self._status.set("Error reading PDF.")
            return
        for p in range(1, n + 1):
            self._pages_lb.insert(tk.END, f"Page {p}")
        self._status.set(f"{n} page(s) — {path}")

    def _current_file_path(self) -> str | None:
        sel = self._files_lb.curselection()
        if not sel or not self._files:
            return None
        i = sel[0]
        return self._files[i] if i < len(self._files) else None

    def _save_extract(self) -> None:
        path = self._current_file_path()
        if not path:
            messagebox.showinfo("Extract", "Select a PDF in the file list first.")
            return
        picks = [int(i) + 1 for i in self._pages_lb.curselection()]
        if not picks:
            messagebox.showinfo("Extract", "Select one or more pages in the page list.")
            return
        out = filedialog.asksaveasfilename(
            title="Save extracted pages",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("All files", "*.*")],
        )
        if not out:
            return
        try:
            extract_pages(path, out, picks)
        except Exception as e:
            messagebox.showerror("Extract failed", str(e))
            return
        self._status.set(f"Saved: {out}")
        messagebox.showinfo("Extract", "Done.")

    def _save_merge(self) -> None:
        if not self._files:
            messagebox.showinfo("Merge", "Add at least one PDF to the list.")
            return
        out = filedialog.asksaveasfilename(
            title="Save merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("All files", "*.*")],
        )
        if not out:
            return
        try:
            merge_pdfs(self._files, out)
        except Exception as e:
            messagebox.showerror("Merge failed", str(e))
            return
        self._status.set(f"Merged to: {out}")
        messagebox.showinfo("Merge", "Done.")


def main() -> None:
    app = PdfToolApp()
    app.mainloop()


if __name__ == "__main__":
    main()
