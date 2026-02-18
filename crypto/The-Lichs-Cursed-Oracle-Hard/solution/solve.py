#!/usr/bin/env python3
"""Solve script for The Lich's Cursed Oracle — CBC bit-flipping attack."""

from pwn import *

HOST = "localhost"
PORT = 1337


def solve():
    r = remote(HOST, PORT)

    # Receive the banner and token
    r.recvuntil(b"IV:  ")
    iv_hex = r.recvline().strip().decode()
    r.recvuntil(b"CT:  ")
    ct_hex = r.recvline().strip().decode()

    iv = bytes.fromhex(iv_hex)
    ct = bytes.fromhex(ct_hex)

    # Plaintext: "role=guest;name=adventurer;access=vault"
    # We want:   "role=admin;name=adventurer;access=vault"
    #
    # In CBC, plaintext[i] = decrypt(ct[i]) XOR ct[i-1]
    # For the first block, plaintext[0..15] = decrypt(ct_block0) XOR IV
    #
    # The first block of plaintext is "role=guest;name=" (16 bytes)
    # We want to change "guest" to "admin" at positions 5..9
    #
    # To flip plaintext byte at position j in block 0:
    #   new_iv[j] = iv[j] XOR original_byte XOR target_byte

    original_pt = b"role=guest;name="
    target_pt   = b"role=admin;name="

    new_iv = bytearray(iv)
    for i in range(len(original_pt)):
        if original_pt[i] != target_pt[i]:
            new_iv[i] = iv[i] ^ original_pt[i] ^ target_pt[i]

    # Send forged token
    r.recvuntil(b"> ")
    payload = new_iv.hex() + ":" + ct.hex()
    r.sendline(payload.encode())

    # Receive result
    response = r.recvall(timeout=3).decode()
    print(response)

    r.close()


if __name__ == "__main__":
    solve()
