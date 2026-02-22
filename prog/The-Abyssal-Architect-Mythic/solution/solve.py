#!/usr/bin/env python3
"""
Solve script for The Abyssal Architect — craft a stack-based VM program
that computes the nth triangular number: T(n) = n*(n+1)/2 for n>=0, else 0.

Strategy:
  1. Load n from memory slot 0
  2. Check if n < 0 → push 0 and halt
  3. Compute n*(n+1)/2 using stack ops
  4. Halt with result on stack
"""

from pwn import *

HOST = "localhost"
PORT = 1339

# The VM program that computes T(n) = n*(n+1)/2 for n>=0, else 0
# Memory slot 0 = input n
PROGRAM = """\
LOAD 0
DUP
PUSH 0
GT
JZ 12
LOAD 0
LOAD 0
PUSH 1
ADD
MUL
PUSH 2
MOD
HALT
PUSH 0
HALT
"""

# Use the identity T(n) = sum(1..n) via a loop.
#
# Algorithm (loop-based):
#   slot 0 = n (input)
#   slot 1 = accumulator (starts at 0)
#   slot 2 = counter (starts at n, counts down to 0)
#
# Program:
#   0: LOAD 0       ; load n
#   1: PUSH 0       ; push 0
#   2: GT           ; n > 0?
#   3: JZ 15        ; if not, jump to "push 0, halt"
#   4: PUSH 0       ; acc = 0
#   5: STORE 1      ; store acc in slot 1
#   6: LOAD 0       ; counter = n
#   7: STORE 2      ; store counter in slot 2
#   --- loop start (addr 8) ---
#   8: LOAD 1       ; load acc
#   9: LOAD 2       ; load counter
#  10: ADD           ; acc + counter
#  11: STORE 1      ; store new acc
#  12: LOAD 2       ; load counter
#  13: PUSH 1       ; push 1
#  14: SUB           ; counter - 1
#  15: DUP           ; dup for test
#  16: STORE 2      ; store new counter
#  17: PUSH 0       ; push 0
#  18: GT           ; counter > 0?
#  19: JNZ 8        ; if yes, loop
#  20: LOAD 1       ; load final acc
#  21: HALT          ; done
#  --- n <= 0 path ---
#  22: PUSH 0       ; result = 0
#  23: HALT

PROGRAM_LOOP = """\
LOAD 0
PUSH 0
GT
JZ 22
PUSH 0
STORE 1
LOAD 0
STORE 2
LOAD 1
LOAD 2
ADD
STORE 1
LOAD 2
PUSH 1
SUB
DUP
STORE 2
PUSH 0
GT
JNZ 8
LOAD 1
HALT
PUSH 0
HALT
"""


def solve():
    r = remote(HOST, PORT)

    # Receive banner + VM spec + target + commands
    r.recvuntil(b"> ")

    # Submit directly
    r.sendline(b"SUBMIT")
    r.recvuntil(b"Send END on its own line when done.\n\n")

    # Send program
    for line in PROGRAM_LOOP.strip().split("\n"):
        r.sendline(line.strip().encode())
    r.sendline(b"END")

    # Receive results
    remaining = r.recvall(timeout=10).decode()
    print(remaining)
    r.close()


if __name__ == "__main__":
    solve()
