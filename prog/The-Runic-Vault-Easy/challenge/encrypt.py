def xor_encrypt(plaintext: bytes, key: bytes) -> bytes:
    return bytes([p ^ key[i % len(key)] for i, p in enumerate(plaintext)])

if __name__ == "__main__":
    flag = b"REDACTED"
    key = b"REDACTED"  # 4 lowercase letters
    ciphertext = xor_encrypt(flag, key)
    with open("vault_locked.bin", "wb") as f:
        f.write(ciphertext)
    print("Vault sealed. Contents written to vault_locked.bin")
