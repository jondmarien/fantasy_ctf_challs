FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY shared/ /app/shared/
COPY The-Enchanted-Parrot-Beginner/challenge/ /app/The-Enchanted-Parrot-Beginner/challenge/
COPY The-Whispering-Merchant-Easy/challenge/ /app/The-Whispering-Merchant-Easy/challenge/
COPY The-Court-Wizards-Familiar-Medium/challenge/ /app/The-Court-Wizards-Familiar-Medium/challenge/
COPY The-Oracle-of-Shadows-Hard/challenge/ /app/The-Oracle-of-Shadows-Hard/challenge/
COPY The-Mindflayers-Sanctum-Expert/challenge/ /app/The-Mindflayers-Sanctum-Expert/challenge/
COPY server.py /app/server.py

RUN uv pip install --system --no-cache -r /app/shared/requirements.txt

ENV PYTHONPATH=/app/shared:/app

# Runtime env vars are injected via compose/env files.
ENV RATE_LIMIT=30

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
