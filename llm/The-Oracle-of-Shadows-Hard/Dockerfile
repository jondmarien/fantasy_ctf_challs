FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY shared/ /app/shared/
COPY The-Oracle-of-Shadows-Hard/challenge/ /app/challenge/

RUN uv pip install --system --no-cache -r /app/shared/requirements.txt

ENV PYTHONPATH=/app/shared:/app

EXPOSE 8000

CMD ["uvicorn", "challenge.server:app", "--host", "0.0.0.0", "--port", "8000"]
