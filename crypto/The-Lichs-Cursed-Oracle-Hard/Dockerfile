FROM python:3.12-slim

RUN pip install --no-cache-dir pycryptodome

WORKDIR /app
COPY challenge/oracle.py .

EXPOSE 1337
CMD ["python", "oracle.py"]
