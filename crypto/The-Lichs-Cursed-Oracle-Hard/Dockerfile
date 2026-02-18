FROM python:3.12-slim

RUN pip install --no-cache-dir pycryptodome

ENV FLAG="FantasyCTF{bl0ck_by_bl0ck_th3_ch41n_br34ks}"

WORKDIR /app
COPY challenge/oracle.py .

EXPOSE 1337
CMD ["python", "oracle.py"]
