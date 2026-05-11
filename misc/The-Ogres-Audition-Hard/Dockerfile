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

COPY challenge/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY challenge/ .

ENV FLAG=FantasyCTF{sh3_s4id_d0_y0u_kn0w_th3_muffin_m4n}

RUN chown -R 1001:1001 /app

USER 1001:1001

EXPOSE 1337

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "1337"]
