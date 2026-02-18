# The Dragon's Sealed Proclamation

## Lore

The Dragon Warlord has sealed his war plans using an ancient mathematical enchantment — a lock forged from the product of two prime stones. His court wizard, known for his *small* and *efficient* enchantments, assured the Warlord that the seal was unbreakable.

But whispers in the taverns say otherwise. The wizard's primes were dangerously small, chosen for speed over strength. If you can crack the seal, the Warlord's plans will be laid bare.

## Your Task

You are given the RSA parameters used to seal the proclamation (`params.txt`) and the encryption script (`encrypt.py`). Factor the modulus, recover the private key, and decrypt the ciphertext to obtain the flag.

## Given Files

- `params.txt` — Contains the RSA public key (n, e) and the ciphertext (c)
- `encrypt.py` — The encryption script used by the court wizard

## Flag Format

The flag is in the format: `FantasyCTF{...}`
