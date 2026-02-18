FROM python:3.12-slim

ENV FLAG="FantasyCTF{r3v3rs3_th3_pr0ph3cy_3ng1n3}"

WORKDIR /app
COPY challenge/prophecy_engine.py .

EXPOSE 1337
CMD ["python", "prophecy_engine.py"]
