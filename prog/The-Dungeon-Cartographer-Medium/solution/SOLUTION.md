# Solution: The Dungeon Cartographer

## Category: Prog | Difficulty: Medium | Points: 400

## Overview

Find the minimum-cost path through a weighted grid from the top-left corner to the bottom-right corner using Dijkstra's algorithm. The cost is the flag.

## Clues in the Description

- "the shortest toll" — shortest path problem
- "exact minimum cost to traverse from entrance to exit" — Dijkstra on a weighted grid

## Steps

1. **Parse the grid** — `challenge/dungeon.txt` contains a space-separated grid of integers (cell weights).

2. **Model as a graph** — Each cell `(r, c)` is a node. Moving to an adjacent cell costs that cell's value. Movement is 4-directional (up, down, left, right).

3. **Run Dijkstra's algorithm** — From `(0, 0)` to `(N-1, N-1)`:

   ```python
   import heapq

   dist = [[float('inf')] * n for _ in range(n)]
   dist[0][0] = grid[0][0]
   pq = [(grid[0][0], 0, 0)]

   while pq:
       d, r, c = heapq.heappop(pq)
       if r == n-1 and c == n-1: break
       if d > dist[r][c]: continue
       for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
           nr, nc = r+dr, c+dc
           if 0 <= nr < n and 0 <= nc < n:
               nd = d + grid[nr][nc]
               if nd < dist[nr][nc]:
                   dist[nr][nc] = nd
                   heapq.heappush(pq, (nd, nr, nc))
   ```

4. **Submit the cost as the flag** — `FantasyCTF{<cost>}`

## Solve Script

```bash
python solve.py
```

## Flag

```text
FantasyCTF{1638}
```
