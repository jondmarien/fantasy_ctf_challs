FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY challenge/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY challenge/ .

ENV FLAG=FantasyCTF{sh3_s4id_d0_y0u_kn0w_th3_muffin_m4n}

EXPOSE 80

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
