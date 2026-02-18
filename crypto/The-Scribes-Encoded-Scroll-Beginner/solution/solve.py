import base64
import codecs

def solve():
    with open("../challenge/encoded.txt", "r") as f:
        encoded = f.read().strip()

    # Step 1: Decode Base64
    decoded_bytes = base64.b64decode(encoded).decode()
    # Step 2: Apply ROT13
    flag = codecs.decode(decoded_bytes, 'rot_13')
    print(f"Flag: {flag}")

if __name__ == "__main__":
    solve()
