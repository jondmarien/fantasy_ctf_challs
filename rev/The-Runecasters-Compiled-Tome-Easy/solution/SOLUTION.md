# Solution: The Runecaster's Compiled Tome

## Category: Rev | Difficulty: Easy | Points: 250

## Overview

Decompile a Python bytecode file (`tome.pyc`) to recover the verification logic, then reverse the XOR + permutation shuffle to recover the flag.

## Given Files

- `challenge/tome.pyc` — A compiled Python bytecode file that asks for a passphrase and verifies it.

## Steps

1. **Decompile the bytecode** — Use `uncompyle6`, `pycdc`, or `decompyle3` to recover the source:

   ```bash
   uncompyle6 tome.pyc > tome_decompiled.py
   ```

2. **Analyze the verification logic** — The decompiled code reveals:
   - `KEY = 0x42` — XOR key
   - `PERM` — A permutation array (shuffle order)
   - `ENCRYPTED` — The target encrypted bytes
   - The verification: XOR each input byte with `KEY`, then shuffle using `PERM`, and compare to `ENCRYPTED`

3. **Reverse the transformation**:

   ```python
   KEY = 0x42
   PERM = [23, 33, 3, 11, 10, 35, 28, 30, 31, 22,
           26, 21, 12, 4, 9, 34, 24, 29, 20, 25,
           36, 27, 19, 16, 38, 32, 2, 0, 37, 13,
           18, 5, 6, 8, 14, 15, 17, 1, 7]
   ENCRYPTED = [115, 39, 29, 44, 113, 59, 54, 63, 113, 29,
                35, 54, 42, 29, 33, 114, 35, 38, 32, 113,
                39, 54, 4, 4, 114, 29, 57, 50, 59, 47,
                1, 22, 49, 35, 54, 49, 49, 44, 41]

   # Step 1: Reverse the permutation
   # Forward: shuffled[PERM[i]] = xored[i]
   # Reverse: xored[i] = ENCRYPTED[PERM[i]]
   unshuffled = [ENCRYPTED[PERM[i]] for i in range(len(ENCRYPTED))]

   # Step 2: XOR with key
   flag = "".join(chr(b ^ KEY) for b in unshuffled)
   ```

4. **Get the flag.**

## Solve Script

```bash
python solve.py
```

## Flag

```text
FantasyCTF{th3_t0me_sp3aks_1n_byt3c0de}
```
