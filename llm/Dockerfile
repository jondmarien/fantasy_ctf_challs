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

# Baked-in env vars for CTFd cloud deployment
ENV RATE_LIMIT=30
ENV FLAG_PARROT=FantasyCTF{p0lly_w4nts_4_s3cr3t}
ENV FLAG_MERCHANT=FantasyCTF{m3rch4nt_t0ngu3_sl1pp3d}
ENV FLAG_FAMILIAR=FantasyCTF{f4m1l14r_sp34ks_1n_r1ddl3s}
ENV FLAG_ORACLE=FantasyCTF{sh4d0ws_c4nn0t_h1d3_fr0m_cunn1ng}
ENV FLAG_MINDFLAYER=FantasyCTF{m1ndfl4y3r_b0ws_t0_n0_w4rd}

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
