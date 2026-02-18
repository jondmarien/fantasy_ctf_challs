import base64
import codecs


def encrypt(plaintext: str) -> str:
    # Step 1: Apply ROT13
    rot13_text = codecs.encode(plaintext, "rot_13")
    # Step 2: Encode with Base64
    encoded = base64.b64encode(rot13_text.encode()).decode()
    return encoded


if __name__ == "__main__":
    flag = "REDACTED"
    ciphertext = encrypt(flag)
    with open("encoded.txt", "w") as f:
        f.write(ciphertext)
    print("Encoded scroll written to encoded.txt")
