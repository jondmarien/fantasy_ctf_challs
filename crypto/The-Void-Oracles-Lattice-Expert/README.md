# The Void Oracle's Lattice

## Lore

Beyond the veil of the material plane, the Void Oracle communicates across dimensions using an ancient RSA key exchange. For aeons, its messages were impenetrable — until a flaw was discovered.

The Oracle's private whisper is *brief*, almost unnaturally so, for a being of infinite knowledge. To reduce the latency of cross-dimensional communication, the Oracle chose a private exponent that is far too small. This shortcut has made the Oracle's secrets vulnerable to those who understand the mathematics of continued fractions.

Intercept the Oracle's sealed message and recover its contents.

## Your Task

You are given the RSA public key (n, e) and the ciphertext (c) in `params.txt`, along with the encryption script (`encrypt.py`). The private exponent d is unusually small. Exploit this weakness to recover d and decrypt the message.

## Given Files

- `params.txt` — Contains n, e, and c
- `encrypt.py` — The encryption script

## Flag Format

The flag is in the format: `FantasyCTF{...}`
