FROM python:3.12-slim

ENV FLAG="FantasyCTF{k3ys_4nd_3ch03s_uns34l_th3_d00r}"

WORKDIR /app
COPY challenge/arcane_server.py .

EXPOSE 1337
CMD ["python", "arcane_server.py"]
