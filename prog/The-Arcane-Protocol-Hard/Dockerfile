FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache \
    TMPDIR=/tmp

RUN addgroup --gid 1001 ctf && \
    adduser --uid 1001 --gid 1001 --home /home/ctf --disabled-password --gecos "" ctf

ENV FLAG="FantasyCTF{k3ys_4nd_3ch03s_uns34l_th3_d00r}"

WORKDIR /app
COPY challenge/arcane_server.py .

RUN chown -R 1001:1001 /app

USER 1001:1001

EXPOSE 1337
CMD ["python", "arcane_server.py"]
