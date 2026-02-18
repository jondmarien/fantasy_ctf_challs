# The Arcane Protocol

## Lore

The Arcane Server guards a sealed door deep within the Obsidian Citadel. It speaks a language no adventurer has heard — a binary tongue of keys and echoes, always beginning with a whisper and ending with a seal.

Many have tried to speak to it, but none have answered correctly. The server demands proof that you understand its protocol before it will yield its secret.

## Your Task

Connect to the Arcane Server over TCP. The server will:

1. Send you a greeting and a random nonce (hex-encoded)
2. Expect you to compute the correct response and send it back
3. If your response is correct, it will reveal the flag

You are given the server source code (`arcane_server.py`). Study it to understand the protocol and craft the correct response.

## Given Files

- `arcane_server.py` — The server source code (also running as a Docker service)

## Connection Info

```bash
nc <host> 1337
```

## Flag Format

The flag is in the format: `FantasyCTF{...}`
