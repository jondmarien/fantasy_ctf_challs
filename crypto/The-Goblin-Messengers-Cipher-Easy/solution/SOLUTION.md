# Solution: The Goblin Messenger's Cipher

## Category: Crypto | Difficulty: Easy | Points: 250

## Overview

The ciphertext is encrypted with a Vigenere cipher. The key is hidden in the challenge description as the name of the goblin stronghold: **KARZUL**.

## Clues in the Description

- "the fortress of Karzul guards its secrets well" — the key is `KARZUL`
- "polyalphabetic substitution" — confirms Vigenere cipher

## Steps

1. **Read the ciphertext** — Open `challenge/ciphertext.txt`.

2. **Identify the key** — The description mentions "the fortress of Karzul" — this is the Vigenere key.

3. **Decrypt with Vigenere** — Apply standard Vigenere decryption with key `KARZUL`:

   ```python
   def vigenere_decrypt(ciphertext, key):
       key = key.upper()
       result, ki = [], 0
       for c in ciphertext:
           if c.isalpha():
               shift = ord(key[ki % len(key)]) - ord('A')
               base = ord('A') if c.isupper() else ord('a')
               result.append(chr((ord(c) - base - shift) % 26 + base))
               ki += 1
           else:
               result.append(c)
       return ''.join(result)

   flag = vigenere_decrypt(ciphertext, "KARZUL")
   ```

4. **Get the flag.**

## Solve Script

```bash
python solve.py
```

## Flag

```text
FantasyCTF{g0bl1n_c1ph3r_cr4ck3d_by_k4rzul}
```
