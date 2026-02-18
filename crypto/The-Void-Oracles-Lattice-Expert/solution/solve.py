#!/usr/bin/env python3
"""Solve script for The Void Oracle's Lattice — Wiener's attack on RSA with small d."""


def continued_fraction(e, n):
    """Compute the continued fraction expansion of e/n."""
    cf = []
    while n:
        q, r = divmod(e, n)
        cf.append(q)
        e, n = n, r
    return cf


def convergents(cf):
    """Generate convergents (k/d) from a continued fraction expansion."""
    h_prev, h_curr = 0, 1
    k_prev, k_curr = 1, 0
    for a in cf:
        h_prev, h_curr = h_curr, a * h_curr + h_prev
        k_prev, k_curr = k_curr, a * k_curr + k_prev
        yield h_curr, k_curr


def wiener_attack(e, n):
    """Attempt to recover d using Wiener's attack."""
    from math import isqrt

    cf = continued_fraction(e, n)
    for k, d in convergents(cf):
        if k == 0:
            continue
        # Check if (e*d - 1) is divisible by k
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        # phi = n - p - q + 1, so p + q = n - phi + 1
        s = n - phi + 1
        # p and q are roots of x^2 - s*x + n = 0
        discriminant = s * s - 4 * n
        if discriminant < 0:
            continue
        t = isqrt(discriminant)
        if t * t == discriminant:
            return d
    return None


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

    print("Attempting Wiener's attack...")
    d = wiener_attack(e, n)

    if d is None:
        print("Wiener's attack failed.")
        return

    print(f"Recovered d = {d}")

    # Decrypt
    plaintext_int = pow(c, d, n)
    plaintext = plaintext_int.to_bytes((plaintext_int.bit_length() + 7) // 8, 'big').decode()
    print(f"Flag: {plaintext}")


if __name__ == "__main__":
    solve()
