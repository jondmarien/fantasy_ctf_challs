# Solution: The Runic Vault

## Category: Prog | Difficulty: Easy | Points: 250

## Overview

The vault contents are encrypted with a repeating-key XOR cipher using a 4-character lowercase key. Brute-force all 26^4 possible keys and check for the known flag prefix.

## Clues in the Description

- "four letters, no more, no less" — key length is 4
- "tongue of commoners" — lowercase letters only (a-z)

## Steps

1. **Read the ciphertext** — `challenge/vault_locked.bin` is the XOR-encrypted binary file.

2. **Brute-force the key** — Try all 456,976 combinations of 4 lowercase letters:

   ```python
   import itertools, string

   for combo in itertools.product(string.ascii_lowercase, repeat=4):
       key = "".join(combo).encode()
       decrypted = bytes([c ^ key[i % 4] for i, c in enumerate(ciphertext)])
       if decrypted.startswith(b"FantasyCTF{"):
           print(f"Key: {key.decode()}, Flag: {decrypted.decode()}")
           break
   ```

3. **Get the flag.**

## Solve Script

```bash
python solve.py
```

## Flag

```text
FantasyCTF{run3s_x0r_th3_v4ult_0p3n}
```
