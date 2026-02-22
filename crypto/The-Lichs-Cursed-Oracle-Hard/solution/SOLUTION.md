# Solution: The Lich's Cursed Oracle

## Category: Crypto | Difficulty: Hard | Points: 600

## Overview

This is a **CBC bit-flipping attack**. You receive an AES-CBC encrypted token with `role=guest` and must forge it to read `role=admin` by manipulating the IV.

## Clues in the Description

- "block by block, each piece chained to the last" — AES-CBC mode
- The oracle validates tokens but doesn't reveal plaintext

## Background

In CBC mode, the first plaintext block is computed as:

```
P[0] = Decrypt(C[0]) XOR IV
```

By XORing specific bytes in the IV, we can flip the corresponding plaintext bytes without knowing the key.

## Steps

1. **Connect to the oracle** — Receive the intercepted token (IV + ciphertext in hex).

2. **Identify the target bytes** — The plaintext is `role=guest;name=adventurer;access=vault`. We need to change `guest` (bytes 5-9) to `admin`.

3. **Compute the forged IV** — For each byte position `j` where the plaintext differs:

   ```python
   new_iv[j] = iv[j] ^ original_byte[j] ^ target_byte[j]
   ```

   Specifically, flip bytes 5-9 to change `guest` → `admin`:

   ```python
   original_pt = b"role=guest;name="
   target_pt   = b"role=admin;name="
   new_iv = bytearray(iv)
   for i in range(len(original_pt)):
       if original_pt[i] != target_pt[i]:
           new_iv[i] = iv[i] ^ original_pt[i] ^ target_pt[i]
   ```

4. **Submit the forged token** — Send `new_iv_hex:ct_hex` to the oracle.

5. **Receive the flag.**

## Solve Script

```bash
pip install pwntools
python solve.py
```

## Flag

```text
FantasyCTF{b1t_fl1pp3d_th3_l1ch5_curs3}
```
