# Solution: The Arcane Protocol

## Category: Prog | Difficulty: Hard | Points: 600

## Overview

Connect to a TCP server that sends a random nonce. Compute an HMAC-SHA256 of the nonce using a secret key found in the server source code, and send it back to receive the flag.

## Clues in the Description

- "riddles of keys and echoes" — keyed hashing (HMAC)
- "beginning with a whisper" — the server sends a nonce first
- "ending with a seal" — you must send back the HMAC

## Steps

1. **Read the server source** — `challenge/arcane_server.py` reveals the hardcoded key:

   ```python
   ARCANE_KEY = b"ObsidianCitadel_S3cretKey_2024"
   ```

2. **Connect to the server** — It sends a greeting and a hex-encoded random nonce.

3. **Compute HMAC-SHA256** of the nonce using the key:

   ```python
   import hmac, hashlib
   seal = hmac.new(ARCANE_KEY, nonce.encode(), hashlib.sha256).hexdigest()
   ```

4. **Send the seal** — The server validates it and returns the flag.

## Solve Script

```bash
pip install pwntools
python solve.py
```

## Flag

```text
FantasyCTF{k3ys_4nd_3ch03s_uns34l_th3_d00r}
```
