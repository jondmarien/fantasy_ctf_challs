FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache \
    TMPDIR=/tmp

RUN addgroup --gid 1001 ctf && \
    adduser --uid 1001 --gid 1001 --home /home/ctf --disabled-password --gecos "" ctf

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY shared/ /app/shared/
COPY The-Mindflayers-Sanctum-Expert/challenge/ /app/challenge/

RUN uv pip install --system --no-cache -r /app/shared/requirements.txt

ENV PYTHONPATH=/app/shared:/app

RUN chown -R 1001:1001 /app

USER 1001:1001

EXPOSE 8000

CMD ["uvicorn", "challenge.server:app", "--host", "0.0.0.0", "--port", "8000"]
