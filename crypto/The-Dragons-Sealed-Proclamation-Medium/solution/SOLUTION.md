# Solution: The Dragon's Sealed Proclamation

## Category: Crypto | Difficulty: Medium | Points: 400

## Overview

The RSA encryption uses a **deterministic prime generation** — the primes are derived from hardcoded seeds visible in `encrypt.py`. Regenerate the same primes to factor `n` and decrypt.

## Clues in the Description

- "small and efficient enchantments" — hints at small, predictable primes
- The vulnerability is in `encrypt.py`, not in the RSA math itself

## Steps

1. **Read the parameters** — `challenge/params.txt` contains `n`, `e`, and `c`.

2. **Examine `encrypt.py`** — The script reveals the exact prime generation:

   ```python
   p = nextprime(2**200 + 1337)
   q = nextprime(2**201 + 7331)
   ```

3. **Regenerate the primes** — Since the seeds are hardcoded, we can compute the same primes:

   ```python
   from sympy import nextprime
   p = nextprime(2**200 + 1337)
   q = nextprime(2**201 + 7331)
   assert p * q == n
   ```

4. **Compute the private key and decrypt**:

   ```python
   phi = (p - 1) * (q - 1)
   d = pow(e, -1, phi)
   plaintext_int = pow(c, d, n)
   flag = plaintext_int.to_bytes((plaintext_int.bit_length() + 7) // 8, "big").decode()
   ```

5. **Get the flag.**

## Solve Script

```bash
pip install sympy
python solve.py
```

## Flag

```text
FantasyCTF{d3t3rm1n1st1c_pr1m3s_4r3_n0_d3f3ns3}
```
