# Solution: The Prophecy Engine

## Category: Prog | Difficulty: Expert | Points: 1000

## Overview

The server applies a secret 3-stage transformation to inputs. Use the ORACLE command to probe the function, deduce each stage, then invert the transformation to solve the CHALLENGE.

## Clues in the Description

- "transforms what you give it, step by step" — multi-stage function
- "recursive" — each stage feeds into the next
- Source code (`prophecy_engine.py`) is provided, revealing the transformation

## The Transformation

From the source code:

```python
# Stage 1: Modular multiplication
x = (x * 7) % 65537
# Stage 2: XOR with constant
x = x ^ 0xDEAD
# Stage 3: Addition
x = x + 31337
```

## Steps

1. **Connect and request CHALLENGE** — The server gives a target output value.

2. **Reverse the transformation** — Invert each stage in reverse order:

   ```python
   # Reverse Stage 3: subtract constant
   x = target - 31337
   # Reverse Stage 2: XOR (self-inverse)
   x = x ^ 0xDEAD
   # Reverse Stage 1: modular multiplicative inverse
   inv = pow(7, -1, 65537)
   x = (x * inv) % 65537
   ```

3. **Send the answer** — Submit the computed input to receive the flag.

## Discovery Approach (Without Source)

If the source weren't provided, you would:

1. Send `ORACLE 0`, `ORACLE 1`, `ORACLE 2`, etc. to observe outputs
2. Notice the constant offset (Stage 3) from `ORACLE 0`
3. Subtract the offset and XOR patterns become visible (Stage 2)
4. Identify the modular multiplication from the linear relationship (Stage 1)

## Solve Script

```bash
pip install pwntools
python solve.py
```

## Flag

```text
FantasyCTF{r3v3rs3_th3_pr0ph3cy_3ng1n3}
```
