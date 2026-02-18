# The Runic Vault

## Lore

Deep beneath the Runekeeper's Tower lies a vault sealed by an ancient four-letter word of power. The vault keeper was known to only use lowercase letters of the common tongue — four letters, no more, no less, in the tongue of commoners.

The vault's contents were encrypted with a repeating-key XOR cipher using this word. A fragment of the encrypted treasure has been recovered. Break the seal and claim what lies within.

## Your Task

You are given the encrypted vault contents (`vault_locked.bin`) and the encryption script (`encrypt.py`). The key is a 4-character lowercase alphabetic string. Brute-force the key to recover the flag.

## Given Files

- `vault_locked.bin` — The XOR-encrypted vault contents
- `encrypt.py` — The encryption script used to seal the vault

## Flag Format

The flag is in the format: `FantasyCTF{...}`
