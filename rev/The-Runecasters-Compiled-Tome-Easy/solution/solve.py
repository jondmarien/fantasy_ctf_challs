"""
Solution for The Runecaster's Compiled Tome (Easy Rev)
1. Decompile tome.pyc to recover KEY, PERM, and ENCRYPTED
2. Reverse the permutation shuffle
3. XOR with the key to recover the flag
"""


def solve():
    # Values extracted from decompiled tome.pyc
    KEY = 0x42

    PERM = [
        23, 33, 3, 11, 10, 35, 28, 30, 31, 22,
        26, 21, 12, 4, 9, 34, 24, 29, 20, 25,
        36, 27, 19, 16, 38, 32, 2, 0, 37, 13,
        18, 5, 6, 8, 14, 15, 17, 1, 7,
    ]

    ENCRYPTED = [
        115, 39, 29, 44, 113, 59, 54, 63, 113, 29,
        35, 54, 42, 29, 33, 114, 35, 38, 32, 113,
        39, 54, 4, 4, 114, 29, 57, 50, 59, 47,
        1, 22, 49, 35, 54, 49, 49, 44, 41,
    ]

    # Step 1: Reverse the permutation
    # Forward: shuffled[PERM[i]] = xored[i]
    # Reverse: xored[i] = shuffled[PERM[i]]  (i.e., ENCRYPTED[PERM[i]])
    unshuffled = [ENCRYPTED[PERM[i]] for i in range(len(ENCRYPTED))]

    # Step 2: XOR with key to recover plaintext
    flag = "".join(chr(b ^ KEY) for b in unshuffled)

    print(f"Flag: {flag}")


if __name__ == "__main__":
    solve()
