FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache \
    TMPDIR=/tmp

RUN addgroup --gid 1001 ctf && \
    adduser --uid 1001 --gid 1001 --home /home/ctf --disabled-password --gecos "" ctf

ENV FLAG="FantasyCTF{r3v3rs3_th3_pr0ph3cy_3ng1n3}"

WORKDIR /app
COPY challenge/prophecy_engine.py .

RUN chown -R 1001:1001 /app

USER 1001:1001

EXPOSE 1337
CMD ["python", "prophecy_engine.py"]
