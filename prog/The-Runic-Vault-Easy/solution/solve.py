#!/usr/bin/env python3
"""Solve script for The Runic Vault — brute-force 4-char lowercase XOR key."""

import itertools
import string


def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    return bytes([c ^ key[i % len(key)] for i, c in enumerate(ciphertext)])


def solve():
    with open("../challenge/vault_locked.bin", "rb") as f:
        ciphertext = f.read()

    prefix = b"FantasyCTF{"

    for combo in itertools.product(string.ascii_lowercase, repeat=4):
        key = "".join(combo).encode()
        decrypted = xor_decrypt(ciphertext, key)
        if decrypted.startswith(prefix):
            print(f"Key found: {key.decode()}")
            print(f"Flag: {decrypted.decode()}")
            return

    print("No valid key found.")


if __name__ == "__main__":
    solve()
