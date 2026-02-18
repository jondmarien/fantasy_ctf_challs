#!/usr/bin/env python3
"""
Solve script for The Prophecy Engine — reverse-engineer the black-box transformation.

The transformation is: f(x) = ((x * 7) % 65537) XOR 0xDEAD + 31337

To reverse:
  1. Subtract 31337 from target
  2. XOR with 0xDEAD
  3. Multiply by modular inverse of 7 mod 65537

Discovery approach (how a player would figure this out):
  - Send ORACLE 0, ORACLE 1, ORACLE 2, ... to observe patterns
  - Stage 3 (addition) is visible as a constant offset: f(0) gives the base
  - Stage 2 (XOR) can be deduced by comparing f(0) vs expected after removing offset
  - Stage 1 (modular multiplication) can be deduced from f(1) - f(0) patterns
    and by noting the modular wraparound at 65537
"""

from pwn import *

HOST = "0.cloud.chals.io"
PORT = 26408

# Constants deduced from probing the oracle
STAGE1_MULT = 7
STAGE1_MOD = 65537
STAGE2_XOR = 0xDEAD
STAGE3_ADD = 31337


def inverse_transform(target: int) -> int:
    """Reverse the 3-stage transformation."""
    # Reverse Stage 3: subtract constant
    x = target - STAGE3_ADD
    # Reverse Stage 2: XOR (self-inverse)
    x = x ^ STAGE2_XOR
    # Reverse Stage 1: modular multiplicative inverse
    inv_mult = pow(STAGE1_MULT, -1, STAGE1_MOD)
    x = (x * inv_mult) % STAGE1_MOD
    return x


def solve():
    r = remote(HOST, PORT)

    # Get the challenge target
    r.sendlineafter(b"> ", b"CHALLENGE")
    r.recvuntil(b"TARGET: ")
    target = int(r.recvline().strip().decode())
    log.info(f"Target: {target}")

    # Compute the inverse
    answer = inverse_transform(target)
    log.info(f"Computed input: {answer}")

    # Send answer
    r.recvuntil(b"ANSWER: ")
    r.sendline(str(answer).encode())

    # Receive result
    response = r.recvall(timeout=3).decode()
    print(response)

    r.close()


if __name__ == "__main__":
    solve()
