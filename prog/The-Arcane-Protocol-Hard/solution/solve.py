#!/usr/bin/env python3
"""Solve script for The Arcane Protocol — HMAC-SHA256 handshake."""

from pwn import *
import hmac
import hashlib

HOST = "0.cloud.chals.io"
PORT = 12292

# Key extracted from arcane_server.py source code
ARCANE_KEY = b"ObsidianCitadel_S3cretKey_2024"


def solve():
    r = remote(HOST, PORT)

    # Receive greeting and nonce
    r.recvuntil(b"NONCE: ")
    nonce = r.recvline().strip().decode()
    log.info(f"Received nonce: {nonce}")

    # Compute HMAC-SHA256
    seal = hmac.new(ARCANE_KEY, nonce.encode(), hashlib.sha256).hexdigest()
    log.info(f"Computed seal: {seal}")

    # Send response
    r.recvuntil(b"> ")
    r.sendline(seal.encode())

    # Receive result
    response = r.recvall(timeout=3).decode()
    print(response)

    r.close()


if __name__ == "__main__":
    solve()
