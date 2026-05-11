FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache \
    TMPDIR=/tmp

RUN addgroup --gid 1001 ctf && \
    adduser --uid 1001 --gid 1001 --home /home/ctf --disabled-password --gecos "" ctf

WORKDIR /app

COPY The-Chronomancers-Gauntlet-Legendary/challenge/ /app/The-Chronomancers-Gauntlet-Legendary/challenge/
COPY The-Abyssal-Architect-Mythic/challenge/ /app/The-Abyssal-Architect-Mythic/challenge/
COPY server.py /app/server.py

# Baked-in env vars for CTFd cloud deployment
ENV FLAG_CHRONOMANCER=FantasyCTF{t1m3_b3nds_t0_th3_sw1ft_m1nd}
ENV FLAG_ARCHITECT=FantasyCTF{th3_4byss_y13lds_t0_1ts_4rch1t3ct}

RUN chown -R 1001:1001 /app

USER 1001:1001

EXPOSE 1338

CMD ["python", "server.py"]
