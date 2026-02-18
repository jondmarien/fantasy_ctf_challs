def vigenere_decrypt(ciphertext: str, key: str) -> str:
    key = key.upper()
    result = []
    key_index = 0
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            if char.isupper():
                decrypted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                decrypted = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            result.append(decrypted)
            key_index += 1
        else:
            result.append(char)
    return ''.join(result)

def solve():
    with open("../challenge/ciphertext.txt", "r") as f:
        ciphertext = f.read().strip()

    key = "KARZUL"
    flag = vigenere_decrypt(ciphertext, key)
    print(f"Flag: {flag}")

if __name__ == "__main__":
    solve()
