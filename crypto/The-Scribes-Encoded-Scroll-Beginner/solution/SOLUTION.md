# Solution: The Scribe's Encoded Scroll

## Category: Crypto | Difficulty: Beginner | Points: 100

## Overview

The scribe encoded his message using two layers: Base64 followed by ROT13. Reverse both to recover the flag.

## Clues in the Description

- "sixty-four runes of an old alphabet" = Base64
- "rOtation of letters" = ROT13 (the capital O is a hint)

## Steps

1. **Read the encoded file** — Open `challenge/encoded.txt` to get the encoded string.

2. **Decode Base64** — The outer layer is Base64 encoding:

   ```python
   import base64
   decoded = base64.b64decode(encoded).decode()
   ```

3. **Apply ROT13** — The inner layer is a ROT13 substitution cipher:

   ```python
   import codecs
   flag = codecs.decode(decoded, 'rot_13')
   ```

4. **Get the flag.**

## Solve Script

```bash
python solve.py
```

## Flag

```text
FantasyCTF{th3_scr1b3s_r0t4t10n_b3tr4y3d_h1m}
```
