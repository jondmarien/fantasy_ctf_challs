from sympy import nextprime, mod_inverse

def generate_wiener_vulnerable_rsa():
    # Large primes, but dangerously small private exponent
    p = nextprime(2**512 + 12345)
    q = nextprime(2**512 + 67890)
    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose a small d — this makes e very large and vulnerable to Wiener's attack
    d = nextprime(2**64)
    e = mod_inverse(d, phi)

    return n, e

def encrypt(plaintext: str, n: int, e: int) -> int:
    plaintext_int = int.from_bytes(plaintext.encode(), 'big')
    ciphertext = pow(plaintext_int, e, n)
    return ciphertext

if __name__ == "__main__":
    n, e = generate_wiener_vulnerable_rsa()
    flag = "REDACTED"
    c = encrypt(flag, n, e)

    with open("params.txt", "w") as f:
        f.write(f"n = {n}\n")
        f.write(f"e = {e}\n")
        f.write(f"c = {c}\n")

    print("RSA parameters written to params.txt")
