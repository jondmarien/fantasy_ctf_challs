# Solution: The Guild Ledger

## Category: Prog | Difficulty: Beginner | Points: 100

## Overview

Parse a CSV ledger file, find the single entry whose `gold_amount` is a prime number, and Base64-decode its `notes` field to get the flag.

## Clues in the Description

- "only a prime adventurer could spot this entry" — look for a prime `gold_amount`
- "the fraudster hid a message in the notes field" — the flag is Base64-encoded in `notes`

## Steps

1. **Parse the ledger** — `challenge/ledger.txt` is a CSV file with columns including `gold_amount` and `notes`.

2. **Find the prime entry** — Iterate through all rows and check if `gold_amount` is prime:

   ```python
   from math import isqrt

   def is_prime(n):
       if n < 2: return False
       if n < 4: return True
       if n % 2 == 0 or n % 3 == 0: return False
       i = 5
       while i <= isqrt(n):
           if n % i == 0 or n % (i + 2) == 0: return False
           i += 6
       return True
   ```

3. **Decode the notes** — The matching row's `notes` field is Base64-encoded:

   ```python
   import base64
   flag = base64.b64decode(notes_b64).decode()
   ```

4. **Get the flag.**

## Solve Script

```bash
python solve.py
```

## Flag

```text
FantasyCTF{pr1m3_b0unty_unm4sks_th3_fr4ud}
```
