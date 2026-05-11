FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache \
    TMPDIR=/tmp

RUN addgroup --gid 1001 ctf && \
    adduser --uid 1001 --gid 1001 --home /home/ctf --disabled-password --gecos "" ctf

RUN pip install --no-cache-dir pycryptodome

ENV FLAG="FantasyCTF{bl0ck_by_bl0ck_th3_ch41n_br34ks}"

WORKDIR /app
COPY challenge/oracle.py .

RUN chown -R 1001:1001 /app

USER 1001:1001

EXPOSE 1337
CMD ["python", "oracle.py"]
