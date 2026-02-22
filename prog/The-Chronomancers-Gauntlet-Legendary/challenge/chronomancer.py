#!/usr/bin/env python3
"""The Chronomancer's Gauntlet — multi-round timed algorithmic gauntlet server."""

import os
import random
import socket
import threading
import time

FLAG = os.environ.get("FLAG", "FantasyCTF{placeholder}")

# ---------------------------------------------------------------------------
# Round generators — each returns (problem_text, answer)
# ---------------------------------------------------------------------------


def _gen_expression():
    """Round 1: Evaluate a nested arithmetic expression with custom operators.
    @ = modular exponentiation (a @ b = pow(a, b, 10007))
    # = bitwise XOR
    Standard +, -, * also present. No division to avoid floats.
    """
    MOD = 10007

    def _eval_expr(tokens):
        """Simple recursive-descent parser for our mini-language."""
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
                consume()  # '('
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

    # Build a random expression
    ops_outer = ["+", "-", "*"]
    ops_inner = ["@", "#"]

    parts = []
    num_terms = random.randint(4, 6)
    for i in range(num_terms):
        a = random.randint(2, 50)
        b = random.randint(2, 8)
        # Randomly use @ or # for inner sub-expressions
        inner_op = random.choice(ops_inner)
        if random.random() < 0.5:
            parts.append(f"( {a} {inner_op} {b} )")
        else:
            parts.append(str(random.randint(1, 200)))
        if i < num_terms - 1:
            parts.append(random.choice(ops_outer))

    expr_str = " ".join(parts)
    tokens = expr_str.replace("(", "( ").replace(")", " )").split()
    answer = _eval_expr(tokens)

    problem = (
        f"ROUND 1 — THE CHRONOMANCER'S ARITHMETIC\n"
        f"Evaluate this expression. Operators: @ = pow(a,b,10007), # = XOR\n"
        f"Standard +, -, * also apply. Precedence (high→low): @, #, *, +/-\n"
        f"Parentheses override precedence.\n\n"
        f"EXPRESSION: {expr_str}\n\n"
        f"Send the integer result."
    )
    return problem, str(answer)


def _gen_shortest_path():
    """Round 2: Shortest path in a directed weighted graph."""
    n = random.randint(8, 12)
    # Build a connected directed graph
    edges = []
    # Ensure connectivity: chain 0 -> 1 -> ... -> n-1
    for i in range(n - 1):
        w = random.randint(1, 20)
        edges.append((i, i + 1, w))
    # Add random extra edges
    for _ in range(n * 2):
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            w = random.randint(1, 30)
            edges.append((u, v, w))

    src = 0
    dst = n - 1

    # Dijkstra
    import heapq

    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))

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

    answer = dist[dst]

    edge_lines = "\n".join(f"  {u} -> {v} (weight {w})" for u, v, w in edges)
    problem = (
        f"ROUND 2 — THE CHRONOMANCER'S CARTOGRAPHY\n"
        f"Find the shortest path cost from node {src} to node {dst}.\n"
        f"Nodes: 0 to {n - 1}\n"
        f"Directed edges:\n{edge_lines}\n\n"
        f"Send the minimum cost as an integer."
    )
    return problem, str(answer)


def _gen_crt():
    """Round 3: Chinese Remainder Theorem — solve a system of congruences."""
    # Pick 3-4 pairwise coprime moduli
    prime_pool = [3, 5, 7, 11, 13, 17, 19, 23]
    random.shuffle(prime_pool)
    num_eq = random.randint(3, 4)
    moduli = prime_pool[:num_eq]

    # Pick a secret value
    M = 1
    for m in moduli:
        M *= m
    secret = random.randint(1, M - 1)
    remainders = [secret % m for m in moduli]

    # CRT solution
    def _solve_crt(rems, mods):
        N = 1
        for m in mods:
            N *= m
        result = 0
        for r, m in zip(rems, mods):
            Ni = N // m
            Mi = pow(Ni, -1, m)
            result += r * Ni * Mi
        return result % N

    answer = _solve_crt(remainders, moduli)

    eq_lines = "\n".join(f"  x ≡ {r} (mod {m})" for r, m in zip(remainders, moduli))
    problem = (
        f"ROUND 3 — THE CHRONOMANCER'S CONGRUENCES\n"
        f"Solve this system of linear congruences for x (smallest positive):\n"
        f"{eq_lines}\n\n"
        f"Send the value of x as an integer."
    )
    return problem, str(answer)


def _gen_determinant():
    """Round 4: Determinant of an NxN matrix modulo a prime."""
    P = 10007
    n = random.randint(4, 5)

    matrix = [[random.randint(0, P - 1) for _ in range(n)] for _ in range(n)]

    # Compute determinant mod P via Gaussian elimination
    def _det_mod(mat, p):
        sz = len(mat)
        m = [row[:] for row in mat]
        det = 1
        for col in range(sz):
            # Find pivot
            pivot = -1
            for row in range(col, sz):
                if m[row][col] % p != 0:
                    pivot = row
                    break
            if pivot == -1:
                return 0
            if pivot != col:
                m[col], m[pivot] = m[pivot], m[col]
                det = (-det) % p
            det = (det * m[col][col]) % p
            inv = pow(m[col][col], -1, p)
            for row in range(col + 1, sz):
                factor = (m[row][col] * inv) % p
                for k in range(col, sz):
                    m[row][k] = (m[row][k] - factor * m[col][k]) % p
        return det % p

    answer = _det_mod(matrix, P)

    mat_lines = "\n".join("  " + " ".join(f"{v:5d}" for v in row) for row in matrix)
    problem = (
        f"ROUND 4 — THE CHRONOMANCER'S MATRIX\n"
        f"Compute the determinant of this {n}x{n} matrix modulo {P}.\n\n"
        f"Matrix:\n{mat_lines}\n\n"
        f"Send the determinant (mod {P}) as an integer (0 to {P - 1})."
    )
    return problem, str(answer)


def _gen_knapsack():
    """Round 5: 0/1 Knapsack."""
    n = random.randint(15, 20)
    max_w = random.randint(50, 80)
    items = []
    for _ in range(n):
        w = random.randint(1, 25)
        v = random.randint(1, 100)
        items.append((w, v))

    # DP solve
    dp = [0] * (max_w + 1)
    for w, v in items:
        for c in range(max_w, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    answer = dp[max_w]

    item_lines = "\n".join(
        f"  Item {i}: weight={w}, value={v}" for i, (w, v) in enumerate(items)
    )
    problem = (
        f"ROUND 5 — THE CHRONOMANCER'S HOARD\n"
        f"You have a pack with capacity {max_w}.\n"
        f"Select items to maximize total value (each item used at most once).\n\n"
        f"Items:\n{item_lines}\n\n"
        f"Send the maximum achievable value as an integer."
    )
    return problem, str(answer)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

ROUNDS = [
    _gen_expression,
    _gen_shortest_path,
    _gen_crt,
    _gen_determinant,
    _gen_knapsack,
]
TIME_LIMIT = 5  # seconds per round


def handle_client(conn: socket.socket, addr):
    try:
        conn.settimeout(60)
        conn.sendall(b"=== The Chronomancer's Gauntlet ===\n")
        conn.sendall(b"Five trials await. Each must be answered within 5 seconds.\n")
        conn.sendall(b"Fail one, and the sands consume you.\n\n")

        for i, gen_fn in enumerate(ROUNDS):
            problem, answer = gen_fn()
            conn.sendall(f"{problem}\n\n".encode())
            conn.sendall(b"ANSWER> ")

            start = time.time()
            try:
                data = conn.recv(4096).decode().strip()
            except socket.timeout:
                conn.sendall(b"\nTime expired. The sands consume you.\n")
                return

            elapsed = time.time() - start
            if elapsed > TIME_LIMIT:
                conn.sendall(b"\nToo slow. The sands consume you.\n")
                return

            if data == answer:
                conn.sendall(f"Correct! ({elapsed:.2f}s)\n\n".encode())
            else:
                conn.sendall(f"\nWrong. Expected {answer}, got {data}.\n".encode())
                conn.sendall(b"The Gauntlet rejects you.\n")
                return

        conn.sendall(b"=== ALL TRIALS COMPLETE ===\n")
        conn.sendall(b"The Chronomancer bows. Time itself yields to your mind.\n")
        conn.sendall(f"Flag: {FLAG}\n".encode())

    except Exception as e:
        try:
            conn.sendall(f"Gauntlet error: {e}\n".encode())
        except Exception:
            pass
    finally:
        conn.close()


def main(port=1338):
    host = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Chronomancer's Gauntlet listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    main()
