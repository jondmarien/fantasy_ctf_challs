#!/usr/bin/env python3
"""The Dungeon Cartographer — load the grid and check the player's answer."""

import os

FLAG = os.environ.get("FLAG", "FantasyCTF{placeholder}")


def load_grid(filename="dungeon.txt"):
    grid = []
    with open(filename, "r") as f:
        for line in f:
            row = list(map(int, line.strip().split()))
            grid.append(row)
    return grid


def main():
    grid = load_grid()
    n = len(grid)
    print("=== The Dungeon Cartographer ===")
    print(f"A {n}x{n} dungeon grid has been loaded.")
    print(f"Find the minimum cost path from (0,0) to ({n - 1},{n - 1}).")
    print("Movement: up, down, left, right only.")
    print("Cost = sum of all cell values along the path (including start and end).")
    print()

    answer = input("Enter the minimum path cost: ").strip()

    expected_flag = FLAG
    if f"FantasyCTF{{{answer}}}" == expected_flag:
        print("\nThe door rumbles open. The treasure is yours.")
        print(f"Flag: {expected_flag}")
    else:
        print("\nThe door remains sealed. That is not the correct toll.")


if __name__ == "__main__":
    main()
