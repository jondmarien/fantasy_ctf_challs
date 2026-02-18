#!/usr/bin/env python3
"""Solve script for The Guild Ledger — find the prime gold_amount entry and decode its notes."""

import csv
import base64
from math import isqrt


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i <= isqrt(n):
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def solve():
    with open("../challenge/ledger.txt", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gold = int(row["gold_amount"])
            if is_prime(gold):
                notes_b64 = row["notes"]
                flag = base64.b64decode(notes_b64).decode()
                print(f"Found prime gold_amount: {gold}")
                print(f"Flag: {flag}")
                return

    print("No prime gold_amount found!")


if __name__ == "__main__":
    solve()
