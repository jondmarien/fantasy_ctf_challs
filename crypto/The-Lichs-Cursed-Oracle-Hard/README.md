# The Lich's Cursed Oracle

## Lore

Deep within the Crypt of Endless Night, the Lich guards access to his vault with an enchanted token system. Each visitor receives an encrypted access token, but only those bearing the mark of `role=admin` may enter.

The Lich's memory is *block* by *block*, each piece *chained* to the last. He trusts his oracle implicitly — it will tell you if your token is valid, but nothing more. The oracle never lies, yet it can be deceived.

You have intercepted a token issued to a lowly `role=guest`. Forge it into one worthy of the vault.

## Your Task

Connect to the oracle service. You are given an intercepted encrypted token and its IV. Modify the ciphertext so that when decrypted, the plaintext reads `role=admin` instead of `role=guest`. Submit the forged token to the oracle to receive the flag.

## Given Files

- `oracle.py` — The oracle server source code
- `challenge.txt` — The intercepted token (IV + ciphertext, hex-encoded)

## Connection Info

```
nc <host> 1337
```

## Flag Format

The flag is in the format: `FantasyCTF{...}`
