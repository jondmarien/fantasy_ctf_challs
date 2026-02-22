# Solution: The Void Oracle's Lattice

## Category: Crypto | Difficulty: Expert | Points: 1000

## Overview

The RSA private exponent `d` is unusually small, making the key vulnerable to **Wiener's attack** via continued fraction expansion of `e/n`.

## Clues in the Description

- "private whisper is brief, almost unnaturally so" — `d` is small
- "continued fractions" is the mathematical tool needed

## Background

Wiener's attack exploits RSA keys where `d < n^(1/4) / 3`. The continued fraction expansion of `e/n` produces convergents `k/d` where one of them is the actual private exponent.

## Steps

1. **Read the parameters** — `challenge/params.txt` contains `n`, `e`, and `c`. Note that `e` is very large (close to `n`), which is a telltale sign of small `d`.

2. **Compute the continued fraction expansion of `e/n`**:

   ```python
   def continued_fraction(e, n):
       cf = []
       while n:
           q, r = divmod(e, n)
           cf.append(q)
           e, n = n, r
       return cf
   ```

3. **Generate convergents and test each candidate `d`**:

   ```python
   for k, d in convergents(cf):
       if k == 0: continue
       if (e * d - 1) % k != 0: continue
       phi = (e * d - 1) // k
       # Verify: p + q = n - phi + 1, and p*q = n
       s = n - phi + 1
       discriminant = s*s - 4*n
       if discriminant >= 0 and isqrt(discriminant)**2 == discriminant:
           return d  # Found it!
   ```

4. **Decrypt with the recovered `d`**:

   ```python
   plaintext_int = pow(c, d, n)
   flag = plaintext_int.to_bytes((plaintext_int.bit_length() + 7) // 8, 'big').decode()
   ```

5. **Get the flag.**

## Solve Script

```bash
python solve.py
```

## Flag

```text
FantasyCTF{w13n3rs_fr4ct10ns_p13rc3_th3_v01d}
```
