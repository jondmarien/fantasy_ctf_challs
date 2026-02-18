#!/usr/bin/env python3
"""Solve script for The Dungeon Cartographer — Dijkstra shortest path on weighted grid."""

import heapq


def solve():
    # Load grid
    grid = []
    with open("../challenge/dungeon.txt", "r") as f:
        for line in f:
            row = list(map(int, line.strip().split()))
            grid.append(row)

    n = len(grid)

    # Dijkstra from (0,0) to (n-1,n-1)
    dist = [[float('inf')] * n for _ in range(n)]
    dist[0][0] = grid[0][0]
    pq = [(grid[0][0], 0, 0)]

    while pq:
        d, r, c = heapq.heappop(pq)
        if r == n - 1 and c == n - 1:
            break
        if d > dist[r][c]:
            continue
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                nd = d + grid[nr][nc]
                if nd < dist[nr][nc]:
                    dist[nr][nc] = nd
                    heapq.heappush(pq, (nd, nr, nc))

    cost = dist[n - 1][n - 1]
    flag = f"FantasyCTF{{{cost}}}"
    print(f"Minimum path cost: {cost}")
    print(f"Flag: {flag}")


if __name__ == "__main__":
    solve()
