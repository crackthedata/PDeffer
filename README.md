# PDeffer

Small Python helpers to **extract pages** from a PDF and **merge** several PDFs in order:

- **Desktop**: Tkinter UI (`pdf_gui.py`)
- **Self-hosted**: Flask web UI (`web_app.py`) with Docker; PDFs live in a configurable folder (typically a **bind-mounted host directory**)

## Setup

```bash
python -m pip install -r requirements.txt
```

## Web UI (local or Docker)

```bash
mkdir pdfs
python web_app.py
```

Open `http://127.0.0.1:8080`. The app only reads and writes PDFs under its **data directory**:

| Environment | Data directory |
|-------------|----------------|
| Local, default | `./pdfs` (relative to the process working directory) |
| Override | Set `PDEFFER_DATA` to an absolute path |
| Docker image | `/data` (set in the `Dockerfile`; mount your host folder there) |

Upload, extract, merge, and download are confined to that directory (no `..` path escapes).

### Docker (host files via bind mount)

```bash
mkdir pdfs
docker compose up --build
```

Open `http://localhost:8080`. Files in `./pdfs` on the host are visible inside the container as `/data`; new PDFs are written back to the same host folder.

To point at another host directory, change the volume in `docker-compose.yml`, for example:

```yaml
volumes:
  - C:/Users/You/Documents/MyPDFs:/data
```

(Docker Desktop on Windows accepts this style of path.)

For production, set a long random `PDEFFER_SECRET_KEY` in the environment (see `docker-compose.yml`).

**Note:** Tkinter does not run in a typical headless container, so the Docker image serves the **web** app with Gunicorn, not `pdf_gui.py`.

### Removing Docker containers

`docker rm` needs **which** container to remove (name or ID). List them first:

```bash
docker ps -a
```

Then remove one container:

```bash
docker rm NAMES_OR_ID
```

If you started the app with Compose, from this project folder you can stop and remove those containers in one step:

```bash
docker compose down
```

That does **not** delete your host PDF folder (`./pdfs` when using the default bind mount); only the containers go away.

To remove **all** stopped containers on the machine (after Docker’s confirmation):

```bash
docker container prune
```

## Desktop GUI

```bash
python pdf_gui.py
```

- Add PDFs with **Add…**; use **Up** / **Down** to set merge order.
- **Extract pages**: select a file, multi-select pages (Ctrl/Shift), **Save selected pages as new PDF…**.
- **Merge PDFs**: **Merge PDFs** tab → **Merge all into one PDF…**.

## Library usage

```python
from pdf_extract import extract_pages
from pdf_merge import merge_pdfs

extract_pages("input.pdf", "out.pdf", [1, 3, 3, 7])  # 1-based page numbers
merge_pdfs(["a.pdf", "b.pdf"], "combined.pdf")
```

## Requirements

- Python 3.10+
- [pypdf](https://pypdf.readthedocs.io/), Flask, Gunicorn (see `requirements.txt`)
