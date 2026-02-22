#!/usr/bin/env python3
"""
Solve script for The Chronomancer's Gauntlet — automated multi-round algorithmic solver.

Connects to the Gauntlet server and solves all 5 timed rounds:
  1. Expression evaluation with custom operators (@ = pow mod 10007, # = XOR)
  2. Shortest path in a directed weighted graph (Dijkstra)
  3. Chinese Remainder Theorem
  4. Matrix determinant mod 10007
  5. 0/1 Knapsack
"""

from pwn import *
import re
import heapq

HOST = "0.cloud.chals.io"
PORT = 28165  # shared port — both advanced prog challenges on one service


# ---------------------------------------------------------------------------
# Round 1: Expression evaluator
# ---------------------------------------------------------------------------


def solve_expression(expr_str):
    """Parse and evaluate the custom expression."""
    MOD = 10007
    tokens = expr_str.replace("(", "( ").replace(")", " )").split()
    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume():
        t = tokens[pos[0]]
        pos[0] += 1
        return t

    def parse_atom():
        t = peek()
        if t == "(":
            consume()
            val = parse_add()
            consume()  # ')'
            return val
        return int(consume())

    def parse_at():
        val = parse_atom()
        while peek() == "@":
            consume()
            right = parse_atom()
            val = pow(val, right, MOD)
        return val

    def parse_xor():
        val = parse_at()
        while peek() == "#":
            consume()
            right = parse_at()
            val = val ^ right
        return val

    def parse_mul():
        val = parse_xor()
        while peek() == "*":
            consume()
            right = parse_xor()
            val = val * right
        return val

    def parse_add():
        val = parse_mul()
        while peek() in ("+", "-"):
            op = consume()
            right = parse_mul()
            if op == "+":
                val = val + right
            else:
                val = val - right
        return val

    return parse_add()


# ---------------------------------------------------------------------------
# Round 2: Shortest path (Dijkstra)
# ---------------------------------------------------------------------------


def solve_shortest_path(text):
    """Parse graph edges and run Dijkstra."""
    # Extract src, dst
    m = re.search(r"from node (\d+) to node (\d+)", text)
    src, dst = int(m.group(1)), int(m.group(2))

    # Extract node count
    m = re.search(r"Nodes: 0 to (\d+)", text)
    n = int(m.group(1)) + 1

    # Extract edges: "u -> v (weight w)"
    edges = re.findall(r"(\d+) -> (\d+) \(weight (\d+)\)", text)
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[int(u)].append((int(v), int(w)))

    dist = [float("inf")] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))

    return dist[dst]


# ---------------------------------------------------------------------------
# Round 3: Chinese Remainder Theorem
# ---------------------------------------------------------------------------


def solve_crt(text):
    """Parse congruences and solve via CRT."""
    # x ≡ r (mod m)  — note the ≡ is UTF-8
    eqs = re.findall(r"x\s*(?:≡|=)\s*(\d+)\s*\(mod\s*(\d+)\)", text)
    rems = [int(r) for r, _ in eqs]
    mods = [int(m) for _, m in eqs]

    N = 1
    for m in mods:
        N *= m
    result = 0
    for r, m in zip(rems, mods):
        Ni = N // m
        Mi = pow(Ni, -1, m)
        result += r * Ni * Mi
    return result % N


# ---------------------------------------------------------------------------
# Round 4: Matrix determinant mod P
# ---------------------------------------------------------------------------


def solve_determinant(text):
    """Parse matrix and compute determinant mod P."""
    m = re.search(r"modulo (\d+)", text)
    P = int(m.group(1))

    # Extract matrix lines (lines with multiple numbers)
    lines = text.split("\n")
    matrix = []
    for line in lines:
        nums = line.strip().split()
        if len(nums) >= 3:
            try:
                row = [int(x) for x in nums]
                matrix.append(row)
            except ValueError:
                continue

    sz = len(matrix)
    mat = [row[:] for row in matrix]
    det = 1
    for col in range(sz):
        pivot = -1
        for row in range(col, sz):
            if mat[row][col] % P != 0:
                pivot = row
                break
        if pivot == -1:
            return 0
        if pivot != col:
            mat[col], mat[pivot] = mat[pivot], mat[col]
            det = (-det) % P
        det = (det * mat[col][col]) % P
        inv = pow(mat[col][col], -1, P)
        for row in range(col + 1, sz):
            factor = (mat[row][col] * inv) % P
            for k in range(col, sz):
                mat[row][k] = (mat[row][k] - factor * mat[col][k]) % P
    return det % P


# ---------------------------------------------------------------------------
# Round 5: 0/1 Knapsack
# ---------------------------------------------------------------------------


def solve_knapsack(text):
    """Parse items and solve 0/1 knapsack via DP."""
    m = re.search(r"capacity (\d+)", text)
    capacity = int(m.group(1))

    items = re.findall(r"weight=(\d+),\s*value=(\d+)", text)
    items = [(int(w), int(v)) for w, v in items]

    dp = [0] * (capacity + 1)
    for w, v in items:
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

SOLVERS = {
    1: lambda text: solve_expression(
        re.search(r"EXPRESSION:\s*(.+)", text).group(1).strip()
    ),
    2: lambda text: solve_shortest_path(text),
    3: lambda text: solve_crt(text),
    4: lambda text: solve_determinant(text),
    5: lambda text: solve_knapsack(text),
}


def solve():
    r = remote(HOST, PORT)

    # Select challenge from the shared selector menu
    r.recvuntil(b"Select a challenge: ")
    r.sendline(b"1")

    # Receive banner
    r.recvuntil(b"consume you.\n\n")

    for round_num in range(1, 6):
        # Receive problem text until ANSWER>
        problem = r.recvuntil(b"ANSWER> ").decode()
        log.info(f"--- Round {round_num} ---")

        answer = SOLVERS[round_num](problem)
        log.info(f"Answer: {answer}")

        r.sendline(str(answer).encode())

        # Receive response
        resp = r.recvline().decode().strip()
        log.info(f"Response: {resp}")

        if "Correct" not in resp:
            log.error(f"Failed round {round_num}!")
            r.close()
            return

        # Consume blank line between rounds (if not last)
        if round_num < 5:
            r.recvline()

    # Receive flag
    remaining = r.recvall(timeout=3).decode()
    print(remaining)
    r.close()


if __name__ == "__main__":
    solve()
