# Solution: The Chronomancer's Gauntlet

## Category: Prog | Difficulty: Legendary | Points: 250

## Overview

A 5-round timed algorithmic gauntlet over TCP. Each round has a 5-second time limit. You must write an automated solver — manual solving is impossible.

## Rounds

### Round 1 — Expression Evaluation

Evaluate a nested arithmetic expression with custom operators:

- `@` = modular exponentiation: `pow(a, b, 10007)`
- `#` = bitwise XOR

Precedence (high to low): `@`, `#`, `*`, `+`/`-`. Parentheses override.

**Approach**: Write a recursive-descent parser that handles the custom precedence.

### Round 2 — Shortest Path

Given a directed weighted graph as an adjacency list, find the shortest path cost between two nodes.

**Approach**: Parse edges with regex, run Dijkstra's algorithm.

### Round 3 — Chinese Remainder Theorem

Solve a system of linear congruences: `x = r_i (mod m_i)`.

**Approach**: Parse the congruences, apply the standard CRT formula:

```python
N = product(mods)
x = sum(r * (N // m) * pow(N // m, -1, m) for r, m in zip(rems, mods)) % N
```

### Round 4 — Matrix Determinant

Compute the determinant of an NxN matrix modulo a prime.

**Approach**: Gaussian elimination with modular arithmetic.

### Round 5 — 0/1 Knapsack

Given items with weights and values and a capacity, find the maximum value.

**Approach**: Standard dynamic programming:

```python
dp = [0] * (capacity + 1)
for w, v in items:
    for c in range(capacity, w - 1, -1):
        dp[c] = max(dp[c], dp[c - w] + v)
```

## Key Implementation Details

- Use `pwntools` or raw sockets for TCP communication
- Parse each round's problem text with regex to extract parameters
- All 5 rounds must pass in a single connection

## Solve Script

```bash
pip install pwntools
python solve.py
```

## Flag

```text
FantasyCTF{t1m3_b3nds_t0_th3_sw1ft_m1nd}
```
