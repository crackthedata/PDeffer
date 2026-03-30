FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PDEFFER_DATA=/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pdf_extract.py pdf_merge.py page_spec.py paths_safe.py web_app.py ./
COPY templates ./templates
COPY static ./static

RUN mkdir -p /data

EXPOSE 8080

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8080", "web_app:app"]
