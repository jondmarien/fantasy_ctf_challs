from sympy import nextprime

def generate_weak_rsa():
    # The court wizard's "efficient" key generation
    p = nextprime(2**200 + 1337)
    q = nextprime(2**201 + 7331)
    n = p * q
    e = 65537
    return n, e

def encrypt(plaintext: str, n: int, e: int) -> int:
    plaintext_int = int.from_bytes(plaintext.encode(), 'big')
    ciphertext = pow(plaintext_int, e, n)
    return ciphertext

if __name__ == "__main__":
    n, e = generate_weak_rsa()
    flag = "REDACTED"
    c = encrypt(flag, n, e)

    with open("params.txt", "w") as f:
        f.write(f"n = {n}\n")
        f.write(f"e = {e}\n")
        f.write(f"c = {c}\n")

    print("RSA parameters written to params.txt")
