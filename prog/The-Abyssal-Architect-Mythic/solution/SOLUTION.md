# Solution: The Abyssal Architect

## Category: Prog | Difficulty: Mythic | Points: 250

## Overview

Write a program for a custom stack-based virtual machine that computes the nth triangular number: `T(n) = n*(n+1)/2` for `n >= 0`, and `T(n) = 0` for `n < 0`.

## The VM

The Abyssal Engine has ~18 instructions: PUSH, POP, DUP, SWAP, ROT, OVER, ADD, SUB, MUL, MOD, NEG, GT, EQ, JZ, JNZ, LOAD, STORE, HALT. Input `n` is pre-loaded into memory slot 0.

## Strategy

Since the VM has no division instruction, we can't directly compute `n*(n+1)/2`. Instead, use a **loop to sum 1 + 2 + ... + n**:

- Slot 0 = input `n`
- Slot 1 = accumulator (running sum)
- Slot 2 = counter (counts down from `n` to 0)

## The Program

```text
LOAD 0       ; load n
PUSH 0       ; push 0
GT           ; n > 0?
JZ 22        ; if not, jump to "push 0, halt"
PUSH 0       ; acc = 0
STORE 1      ; store acc
LOAD 0       ; counter = n
STORE 2      ; store counter
LOAD 1       ; --- loop start (addr 8) --- load acc
LOAD 2       ; load counter
ADD          ; acc + counter
STORE 1      ; store new acc
LOAD 2       ; load counter
PUSH 1       ; push 1
SUB          ; counter - 1
DUP          ; dup for test
STORE 2      ; store new counter
PUSH 0       ; push 0
GT           ; counter > 0?
JNZ 8        ; if yes, loop back
LOAD 1       ; load final acc
HALT         ; done — result on stack
PUSH 0       ; --- n <= 0 path (addr 22) ---
HALT         ; return 0
```

24 instructions total, well within the 200-instruction limit.

## Steps

1. **Connect to the server** — Read the VM spec and target function.
2. **Use TEST command** (optional) — Verify your program against sample inputs (3 attempts).
3. **Use SUBMIT command** — Send the program line by line, ending with `END`.
4. **Pass all 10 test cases** — The server validates against random inputs including edge cases (0, negative numbers, large positives).

## Solve Script

```bash
pip install pwntools
python solve.py
```

## Flag

```text
FantasyCTF{th3_4byss_y13lds_t0_1ts_4rch1t3ct}
```
