from sympy import nextprime


def solve():
    # Read parameters
    params = {}
    with open("../challenge/params.txt", "r") as f:
        for line in f:
            key, value = line.strip().split(" = ")
            params[key] = int(value)

    n = params["n"]
    e = params["e"]
    c = params["c"]

    # The vulnerability: encrypt.py reveals the exact deterministic prime generation.
    # The wizard used nextprime(2**200 + 1337) and nextprime(2**201 + 7331).
    # We simply regenerate the same primes.
    p = nextprime(2**200 + 1337)
    q = nextprime(2**201 + 7331)
    assert p * q == n, "Factoring failed — primes don't match!"

    # Compute private key
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)

    # Decrypt
    plaintext_int = pow(c, d, n)
    plaintext = plaintext_int.to_bytes(
        (plaintext_int.bit_length() + 7) // 8, "big"
    ).decode()

    print(f"Flag: {plaintext}")


if __name__ == "__main__":
    solve()
