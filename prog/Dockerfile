FROM python:3.12-slim

WORKDIR /app

COPY The-Chronomancers-Gauntlet-Legendary/challenge/ /app/The-Chronomancers-Gauntlet-Legendary/challenge/
COPY The-Abyssal-Architect-Mythic/challenge/ /app/The-Abyssal-Architect-Mythic/challenge/
COPY server.py /app/server.py

# Baked-in env vars for CTFd cloud deployment
ENV FLAG_CHRONOMANCER=FantasyCTF{t1m3_b3nds_t0_th3_sw1ft_m1nd}
ENV FLAG_ARCHITECT=FantasyCTF{th3_4byss_y13lds_t0_1ts_4rch1t3ct}

EXPOSE 1338 1339

CMD ["python", "server.py"]
