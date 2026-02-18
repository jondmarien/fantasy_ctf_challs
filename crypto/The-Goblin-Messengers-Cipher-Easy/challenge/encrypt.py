def vigenere_encrypt(plaintext: str, key: str) -> str:
    key = key.upper()
    result = []
    key_index = 0
    for char in plaintext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            if char.isupper():
                encrypted = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                encrypted = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            result.append(encrypted)
            key_index += 1
        else:
            result.append(char)
    return ''.join(result)

if __name__ == "__main__":
    flag = "REDACTED"
    key = "REDACTED"
    ciphertext = vigenere_encrypt(flag, key)
    with open("ciphertext.txt", "w") as f:
        f.write(ciphertext)
    print("Ciphertext written to ciphertext.txt")
