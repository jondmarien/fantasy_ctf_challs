"""
The Runecaster's Compiled Tome — Easy Rev Challenge
A flag-checking program that XORs + shuffles the input, then compares to a stored blob.
Distributed as .pyc only.
"""

import sys

# XOR key
KEY = 0x42

# Permutation table (shuffle order for a 39-char string)
# Maps: output[PERM[i]] = xored[i]
PERM = [
    23,
    33,
    3,
    11,
    10,
    35,
    28,
    30,
    31,
    22,
    26,
    21,
    12,
    4,
    9,
    34,
    24,
    29,
    20,
    25,
    36,
    27,
    19,
    16,
    38,
    32,
    2,
    0,
    37,
    13,
    18,
    5,
    6,
    8,
    14,
    15,
    17,
    1,
    7,
]

# Pre-computed encrypted blob (generated from the real flag)
ENCRYPTED = [
    115,
    39,
    29,
    44,
    113,
    59,
    54,
    63,
    113,
    29,
    35,
    54,
    42,
    29,
    33,
    114,
    35,
    38,
    32,
    113,
    39,
    54,
    4,
    4,
    114,
    29,
    57,
    50,
    59,
    47,
    1,
    22,
    49,
    35,
    54,
    49,
    49,
    44,
    41,
]


def check_passphrase(user_input):
    if len(user_input) != len(ENCRYPTED):
        return False

    # Step 1: XOR each character with key
    xored = [ord(c) ^ KEY for c in user_input]

    # Step 2: Shuffle using permutation table
    shuffled = [0] * len(xored)
    for i in range(len(xored)):
        shuffled[PERM[i]] = xored[i]

    # Step 3: Compare to stored encrypted blob
    return shuffled == ENCRYPTED


def main():
    print("=" * 50)
    print("  The Runecaster's Compiled Tome")
    print("  Speak the passphrase to unlock the secrets.")
    print("=" * 50)
    print()

    passphrase = input("Enter the passphrase: ")

    if check_passphrase(passphrase):
        print("\n✨ The tome glows with arcane light!")
        print("The tome accepts your passphrase!")
    else:
        print("\n💀 The tome rejects you.")
        print("The runes fade to darkness...")


if __name__ == "__main__":
    main()
